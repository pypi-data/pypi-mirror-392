
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_core.common.exceptions.functional_exception import FunctionalException
import time
import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.common.handlers.object import DeleteableObject
from holado_core.common.tools.tools import Tools
from holado_docker.sdk.docker.container_logs import DockerContainerLogsFollower
import re
from holado_python.common.tools.datetime import DateTime
from holado.common.handlers.undefined import default_value
from holado_core.common.handlers.wait import WaitFuncResult

logger = logging.getLogger(__name__)

try:
    import docker
    with_docker = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"DockerClient is not available. Initialization failed on error: {exc}")
    with_docker = False


class DockerClient(object):
    @classmethod
    def is_available(cls):
        return with_docker
    
    def __init__(self):
        self.__client = docker.from_env()
        self.__containers = {}
        self.__volumes = {}
        
    @property
    def client(self):
        return self.__client
    
    def has_container(self, name, in_list=True, all_=False, reset_if_removed=True):
        # Note: Even if name exists in __containers, it is possible that the container has been removed
        if in_list:
            c = self.__get_container_from_list(name, all_=all_)
            res = c is not None
            
            if reset_if_removed and not res and name in self.__containers:
                del self.__containers[name]
        else:
            res = name in self.__containers
            
            if reset_if_removed and res:
                if self.__containers[name].status == "removed":
                    del self.__containers[name]
                res = False
        return res
    
    def get_container(self, name, all_=False, reset_if_removed=True):
        # Reset container if removed
        if reset_if_removed and name in self.__containers:
            if self.__containers[name].status == "removed":
                del self.__containers[name]
        
        # Get container from list if needed
        if name not in self.__containers:
            c = self.__get_container_from_list(name, all_=all_)
            if c:
                self.__containers[name] = DockerContainer(self, c)
        
        return self.__containers.get(name, None)
    
    def update_containers(self, all_=False, sparse=False, reset_if_removed=True):
        # Add new containers
        updated_names = set()
        for c in self.__client.containers.list(all=all_, sparse=sparse, ignore_removed=True):
            try:
                c_name = c.name
            except docker.errors.NotFound:
                # Container 'c' doesn't exist anymore
                continue
            
            if c_name not in self.__containers:
                self.__containers[c_name] = DockerContainer(self, c)
            updated_names.add(c_name)
            
        if reset_if_removed:
            for name in set(self.__containers.keys()).difference(updated_names):
                del self.__containers[name]
    
    def get_container_names(self, in_list=True, all_=False, sparse=False, include_patterns=None, exclude_patterns=None):
        incl_patterns = [ip if isinstance(ip, re.Pattern) else re.compile(ip) for ip in include_patterns] if include_patterns is not None else None
        excl_patterns = [ep if isinstance(ep, re.Pattern) else re.compile(ep) for ep in exclude_patterns] if exclude_patterns is not None else None

        if in_list:
            res = []
            for c in self.__client.containers.list(all=all_, sparse=sparse, ignore_removed=True):
                try:
                    c_name = c.name
                    if c_name is None:
                        c.reload()
                        c_name = c.name
                except docker.errors.NotFound:
                    # Container 'c' doesn't exist anymore
                    continue
                
                # Manage included and excluded patterns
                if excl_patterns is not None:
                    excluded = False
                    for ep in excl_patterns:
                        if ep.match(c_name):
                            excluded = True
                            break
                    if excluded:
                        continue
                if incl_patterns is not None:
                    included = False
                    for ip in incl_patterns:
                        if ip.match(c_name):
                            included = True
                            break
                    if not included:
                        continue
                
                res.append(c_name)
        else:
            res = list(self.__containers.keys())
        return res
    
    def __get_container_from_list(self, name, all_=False):
        res = None
        for c in self.__client.containers.list(all=all_, ignore_removed=True):
            try:
                c_name = c.name
            except docker.errors.NotFound:
                # Container 'c' doesn't exist anymore
                continue
            
            if c_name == name:
                res = c
                break
        return res
    
    def has_volume(self, name, in_list = False):
        res = name in self.__volumes
        if not res and in_list:
            v = self.__get_volume_from_list(name)
            res = v is not None
        return res
    
    def get_volume(self, name):
        if name not in self.__volumes:
            v = self.__get_volume_from_list(name)
            if v:
                self.__volumes[name] = DockerVolume(v)
        return self.__volumes.get(name)
    
    def get_all_volume_names(self):
        return [v.name for v in self.__client.volumes.list()]
    
    def __get_volume_from_list(self, name):
        res = None
        for v in self.__client.volumes.list():
            if v.name == name:
                res = v
                break
        return res
    
    def run_container(self, name, image, remove_existing=False, wait_running=True, auto_stop=True, **kwargs):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Running docker container '{name}' with image '{image}' and arguments {kwargs}{', and waiting running status' if wait_running else ''}")
        
        # Manage remove if already existing
        cont = self.get_container(name)
        if cont:
            if remove_existing:
                if cont.status == "running":
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Docker container '{name}' is running, stopping it before remove")
                    self.stop_container(name)
                
                if self.has_container(name):    # After stop, container is able to be automatically removed depending on its run parameters 
                    self.remove_container(name)
            else:
                logger.info(f"Docker container '{name}' is already running")
                return
        
        # Run container
        c = self.__client.containers.run(image, name=name, detach=True, **kwargs)
        container = DockerContainer(self, c)
        self.__containers[name] = container
        
        # Manage wait running status
        if wait_running:
            for _ in range(100):
                time.sleep(1)
                if container.status == "running":
                    break
            if container.status != "running":
                raise TechnicalException("Failed to run container of name '{}' (status: {})".format(name, container.status))
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Run docker container '{name}' with image '{image}' and arguments {kwargs}{', and wait running status' if wait_running else ''}")
            
        # Set properties
        container.auto_stop = auto_stop
        
        return container
    
    def restart_container(self, name, wait_running=True, **kwargs):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Restarting docker container '{name}' with arguments {kwargs}{', and waiting running status' if wait_running else ''}")
        container = self.get_container(name)
        if not container:
            raise FunctionalException("Container of name '{}' doesn't exist")
        
        container.restart(**kwargs)
        
        if wait_running:
            for _ in range(120):
                time.sleep(1)
                if container.status == "running":
                    break
            if container.status != "running":
                raise TechnicalException("Failed to restart container of name '{}' (status: {})".format(name, container.status))
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Restarted docker container '{name}' with arguments {kwargs}{', and waited running status' if wait_running else ''}")
    
    def start_container(self, name, wait_running=True, **kwargs):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Starting docker container '{name}' with arguments {kwargs}{', and waiting running status' if wait_running else ''}")
        container = self.get_container(name, all_=True)
        if not container:
            raise FunctionalException("Container of name '{}' doesn't exist")
        
        container.start(**kwargs)
        
        if wait_running:
            for _ in range(120):
                time.sleep(1)
                if container.status == "running":
                    break
            if container.status != "running":
                raise TechnicalException("Failed to start container of name '{}' (status: {})".format(name, container.status))
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Started docker container '{name}' with arguments {kwargs}{', and waited running status' if wait_running else ''}")
        
    def stop_container(self, name):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Stopping docker container of name '{name}'")
        if name not in self.__containers:
            raise FunctionalException("Unknown container of name '{}'".format(name))
        elif self.__containers[name].status != "running":
            raise FunctionalException("Container of name '{}' is not running (status: {})".format(name, self.__containers[name].status))
        
        self.__containers[name].stop()
        try:
            self.__containers[name].wait()
        except docker.errors.NotFound:
            # This exception occurs on containers automatically removed on stop
            pass
        
        if self.__containers[name].status == "running":
            raise FunctionalException("Failed to stop container of name '{}' (status: {})".format(name, self.__containers[name].status))
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Stopped docker container of name '{name}'")
        
    def remove_container(self, name):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Removing docker container of name '{name}'")
        if not self.has_container(name, in_list=True, all_=True):
            raise FunctionalException(f"Container of name '{name}' doesn't exist")
        
        if name in self.__containers:
            del self.__containers[name]
        self.client.api.remove_container(name)
        
        if self.has_container(name, in_list=True, all_=True):
            raise FunctionalException(f"Failed to remove container of name '{name}'")
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Removed docker container of name '{name}'")
    
    def await_container_exists(self, name, timeout=default_value):
        wait_status = WaitFuncResult(f"wait container '{name}' exists", 
                                      lambda: self.has_container(name, in_list=True, all_=True, reset_if_removed=False) )
        wait_status.redo_until(True)
        if timeout is not default_value:
            wait_status.with_timeout(timeout)
        return wait_status.execute()
    
        
class DockerContainer(DeleteableObject):
    def __init__(self, docker_client, container):
        super().__init__(container.name)
        
        self.__docker_client = docker_client
        self.__container = container
        self.__auto_stop = False
        
        # Manage logs
        self.__logs_follower = None
        self.__logs_formatter = None
        
    def _delete_object(self):
        if self.auto_stop and self.status == "running" and self.__docker_client and self.__docker_client.has_container(self.name):
            self.__docker_client.stop_container(self.name)
        
    @property
    def container(self):
        return self.__container
        
    @property
    def information(self):
        try:
            self.__container.reload()
        except docker.errors.NotFound:
            # Container doesn't exist anymore, use last known information
            pass
        return self.__container.attrs
        
    @property
    def status(self):
        """ Container status (created, restarting, running, removing, paused, exited, dead, or removed)
        """
        try:
            self.__container.reload()
        except docker.errors.NotFound:
            return "removed"
        return self.__container.status
        
    @property
    def health_status(self):
        """ Container health status (starting, healthy, unhealthy, or removed).
        """
        try:
            self.__container.reload()
        except docker.errors.NotFound:
            return "removed"
        return self.__container.health
        
    @property
    def auto_stop(self):
        self.__auto_stop
        
    @auto_stop.setter
    def auto_stop(self, auto_stop):
        self.__auto_stop = auto_stop
    
    def reload(self, ignore_removed=True):
        try:
            self.__container.reload()
        except docker.errors.NotFound:
            if not ignore_removed:
                raise
        
    def restart(self, **kwargs):
        return self.__container.restart(**kwargs)
    
    def start(self, **kwargs):
        return self.__container.start(**kwargs)
    
    def stop(self, **kwargs):
        return self.__container.stop(**kwargs)
    
    def wait(self, **kwargs):
        return self.__container.wait(**kwargs)
    
    def await_started(self, timeout=default_value):
        health_status = self.get_health_status()
        if health_status == "healthy":
            return
        elif health_status is not None:
            return self.await_health_status("healthy", timeout=timeout)
        else:
            # Container hasn't healthy mechanism
            return self.await_status("running", timeout=timeout)
            #TODO: for containers that haven't healthy mechanism, add a mechanism to customize how health is computed
    
    def await_status(self, status, timeout=default_value):
        wait_status = WaitFuncResult(f"wait container '{self.name}' has status '{status}'", 
                                      lambda: self.status)
        wait_status.redo_until(status)
        if timeout is not default_value:
            wait_status.with_timeout(timeout)
        return wait_status.execute()
    
    def await_health_status(self, status, timeout=default_value):
        wait_status = WaitFuncResult(f"wait container '{self.name}' has health status '{status}'", 
                                      lambda: self.status)
        wait_status.redo_until(status)
        if timeout is not default_value:
            wait_status.with_timeout(timeout)
        return wait_status.execute()
    
    
    
    # Manage logs
    
    @property
    def is_following_logs(self):
        return self.__logs_follower is not None
    
    @property
    def logs_formatter(self):
        return self.__logs_formatter
    
    @logs_formatter.setter
    def logs_formatter(self, formatter):
        self.__logs_formatter = formatter
    
    def get_container_logs(self, stdout=True, stderr=True, timestamps=False, tail='all', since=None, until=None):
        """ Get logs from Docker Engine
        """
        if isinstance(since, str):
            since = DateTime.str_2_datetime(since)
        if isinstance(until, str):
            until = DateTime.str_2_datetime(until)
            
        logs_bytes = self.__container.logs(stdout=stdout, stderr=stderr, timestamps=timestamps, tail=tail, since=since, until=until)
        return self._get_logs_from_logs_bytes(logs_bytes, with_timestamps=timestamps)
    
    def _get_logs_from_logs_bytes(self, logs_bytes, with_timestamps=False):
        log_bytes_list = logs_bytes.split(b'\n')
        
        res = []
        for log_bytes in log_bytes_list:
            if not log_bytes:
                continue
            res.append(self._get_log_from_log_bytes(log_bytes, with_timestamps))
        
        return res
    
    def _get_log_from_log_bytes(self, log_bytes, with_timestamps=False):
        if with_timestamps:
            t_bytes, log_bytes = log_bytes.split(b' ', maxsplit=1)
            log_time = t_bytes.decode()
        
        try:
            log = log_bytes.decode()
        except:
            log = log_bytes
        
        if with_timestamps:
            res = (log_time, log)
        else:
            res = log
        
        return res
    
    def follow_logs(self, stdout=True, stderr=True, tail='all', since=None):
        """Follow logs from Docker Engine
        """
        if self.__logs_follower is not None:
            raise TechnicalException(f"Logs of container '{self.name}' are already followed")
        
        self.__logs_follower = DockerContainerLogsFollower(self)
        self.__logs_follower.follow_logs(stdout, stderr, tail, since)

    def reset_logs(self):
        """Reset followed logs
        """
        if self.__logs_follower is None:
            raise TechnicalException(f"Logs of container '{self.name}' are not followed")
        
        self.__logs_follower.reset()

    def get_logs(self, stdout=True, stderr=True, timestamps=False, tail='all', since=None, until=None, formatter=None):
        if self.is_following_logs:
            logs = self.__logs_follower.get_logs(stdout=stdout, stderr=stderr, timestamps=timestamps, tail=tail, since=since, until=until)
        else:
            logs = self.get_container_logs(stdout=stdout, stderr=stderr, timestamps=timestamps, tail=tail, since=since, until=until)
        
        formatter = formatter if formatter is not None else self.__logs_formatter
        if formatter is not None:
            res = formatter.format_logs(logs, with_timestamps=timestamps)
        else:
            res = logs
        
        return res




class DockerVolume(object):
    def __init__(self, volume):
        self.__volume = volume
        
    @property
    def volume(self):
        self.__volume
        
    @property
    def attributes(self):
        self.__volume.reload()
        return self.__volume.attrs
    
    def get_attribute(self, attr_path):
        names = attr_path.split('.')
        attrs = self.attributes
        res = attrs
        for i, name in enumerate(names):
            if name in res:
                res = res[name]
            else:
                raise FunctionalException(f"Attribute '{'.'.join(names[:i+1])}' doesn't exist (requested attribute: '{attr_path}' ; volume attributes: {attrs})")
        return res
    
