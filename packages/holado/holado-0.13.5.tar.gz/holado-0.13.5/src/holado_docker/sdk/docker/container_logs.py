
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

import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.common.handlers.object import DeleteableObject
from holado_multitask.multithreading.functionthreaded import FunctionThreaded
from holado_python.common.tools.datetime import DateTime
import json
from holado_json.filesystem.stream_json_file import StreamJSONFile
import re
from holado.common.context.session_context import SessionContext
import os
from datetime import datetime

logger = logging.getLogger(__name__)




class DockerContainerLogsFollower(DeleteableObject):
    """Generic follower of logs of a container
    """
    def __init__(self, docker_container):
        super.__init__(self, docker_container.container.name)
        self.__docker_container = docker_container
        self.__logs = []
        self.__logs_stream = None
    
    def _delete_object(self):
        self.close()
    
    def close(self):
        if self.__logs_stream is not None:
            self.__logs_stream.close()
            self.__thread.join()
            
            self.__logs_stream = None
            self.__thread = None
    
    def follow_logs(self, stdout=True, stderr=True, tail='all', since=None):
        """Follow logs from Docker Engine
        """
        if isinstance(since, str):
            since = DateTime.str_2_datetime(since)
        
        if self.__logs_stream is not None:
            raise TechnicalException(f"Logs of container '{self.name}' are already followed")
        self.__logs_stream = self.__docker_container.container.logs(stdout=stdout, stderr=stderr, tail=tail, since=since, stream=True, timestamps=True)
        
        self.__thread = FunctionThreaded(self.__read_stream, name=f"follow logs of container '{self.__docker_container.container.name}'", register_thread=False)
        self.__thread.interrupt_function = self.__logs_stream.close
        self.__thread.start()
    
    def __read_stream(self):
        for log in self.__logs_stream:
            self.__logs.append( (log['time'], log['steam'] == 'stdout', self.__docker_container._get_log_from_log_bytes(log['log'])) )
    
    def reset(self):
        self.__logs.clear()
    
    def get_logs(self, stdout=True, stderr=True, timestamps=False, tail='all', since=None, until=None):
        if since is not None and isinstance(since, datetime):
            since = DateTime.datetime_2_str(since)
        if until is not None and isinstance(until, datetime):
            until = DateTime.datetime_2_str(until)
        
        res = []
        for log in self.__logs:
            if log[1] and not stdout or not log[1] and not stderr:
                continue
            if since is not None and log[0] < since:
                continue
            if until is not None and log[0] >= until:
                continue
            
            if timestamps:
                res.append( (log[0], log[2]) )
            else:
                res.append(log[2])
        
        if tail != 'all':
            if not isinstance(tail, int) or tail < 0:
                raise TechnicalException(f"Argument 'tail' can be 'all' or a positive integer")
            res = res[-tail:]
        
        return res




class DockerContainerLogsFormatter(object):
    """Base class for formatters of container logs.
    """
    def format_logs(self, logs, with_timestamps=False):
        raise NotImplementedError()

class JsonDockerContainerLogsFormatter(DockerContainerLogsFormatter):
    """Formatter of container logs in JSON format.
    """
    def __init__(self, timestamps_key='time'):
        self.__timestamps_key = timestamps_key
    
    def format_logs(self, logs, with_timestamps=False):
        res = []
        
        for log in logs:
            ts = None
            if with_timestamps:
                ts, log = log[0], log[1]
            
            res_log = {}
            
            # Begin by timestamp so that it is the first dict element
            if ts is not None:
                res_log[self.__timestamps_key] = ts
            
            # Add log as JSON format
            try:
                log_dict = json.loads(log)
            except:
                # In some circumstances (ex: container is in panic), logs can be in another format even if configured in json format
                log_dict = {'log':log}
            res_log.update(log_dict)
            
            res.append(res_log)
        
        return res




class DockerContainerLogsSaver(object):
    """Base class for savers of docker container logs.
    """
    def save_logs(self, docker_container, file_path, stdout=True, stderr=True, timestamps=True, tail='all', since=None, until=None):
        """ Save logs of a container.
        @return: number of logs saved
        """
        raise NotImplementedError()

class JsonDockerContainerLogsSaver(DockerContainerLogsSaver):
    """Saver of docker container logs in a stream JSON file.
    """
    def __init__(self, timestamps_key='time', **dumps_kwargs):
        self.__timestamps_key = timestamps_key
        self.__dumps_kwargs = dumps_kwargs
        
    def save_logs(self, docker_container, file_path, stdout=True, stderr=True, timestamps=True, tail='all', since=None, until=None):
        res = None
        SessionContext.instance().path_manager.makedirs(file_path)
        
        logs = docker_container.get_logs(stdout=stdout, stderr=stderr, timestamps=timestamps, tail=tail, since=since, until=until, 
                                         formatter=JsonDockerContainerLogsFormatter(timestamps_key=self.__timestamps_key))
        if logs:
            with StreamJSONFile(file_path, mode='wt') as fout:
                fout.write_elements_json_object_list(logs)
            res = len(logs)
            logger.info(f"Saved {res} logs for container '{docker_container.container.name}' in file '{file_path}'")
        
        return res


class DockerContainersLogsSaver():
    """Saver of logs for a group of containers
    """
    def __init__(self, docker_client, container_logs_saver=JsonDockerContainerLogsSaver(), include_patterns=None, exclude_patterns=None):
        self.__docker_client = docker_client
        self.__container_logs_saver = container_logs_saver
        self.__include_patterns = [ip if isinstance(ip, re.Pattern) else re.compile(ip) for ip in include_patterns] if include_patterns is not None else None
        self.__exclude_patterns = [ep if isinstance(ep, re.Pattern) else re.compile(ep) for ep in exclude_patterns] if exclude_patterns is not None else None
        
    def save_containers_logs(self, destination_path, stdout=True, stderr=True, timestamps=True, tail='all', since=None, until=None):
        """ Save containers logs
        @return: number of containers for which logs have been saved
        """
        res = 0
        
        names = self.__docker_client.get_container_names(in_list=True, all_=True, sparse=True, include_patterns=self.__include_patterns, exclude_patterns=self.__exclude_patterns)
        for name in names:
            container = self.__docker_client.get_container(name, all_=True, reset_if_removed=False)
            file_path = os.path.join(destination_path, f"{name}.log")
            nb_logs = self.__container_logs_saver.save_logs(container, file_path, stdout=stdout, stderr=stderr, timestamps=timestamps, tail=tail, since=since, until=until)
            
            if nb_logs is not None:
                res += 1
        
        return res

