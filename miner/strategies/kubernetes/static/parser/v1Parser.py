import hashlib
from .k8sParser import K8sParser
from ..errors import WrongFormatError

class V1Parser(K8sParser):

    def __init__(self):
        pass

    @classmethod
    def parse(cls, contentDict: dict, contentStr: str) -> dict:
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'ReplicationController', 'StatefulSet', 'Job']
        info = {}
        try:
            if contentDict['kind'] in workloads and 'template' in contentDict['spec']:
                info = cls._parsePod(contentStr, contentDict['spec']['template']['metadata'], contentDict['spec']['template']['spec'])
            elif contentDict['kind'] == 'Pod':
                info = cls._parsePod(contentStr, contentDict['metadata'], contentDict['spec'])
            elif contentDict['kind'] == 'Service':
                info = cls._parseService(contentDict['metadata'], contentDict['spec'])
            elif contentDict['kind'] == 'Endpoints':
                info = cls._parseEndpoints(contentDict['metadata'], contentDict['spec'])
        except:
            raise WrongFormatError('')
        return info

    @classmethod
    def _parsePod(cls, contentStr: str, metadata: dict, spec: dict) -> {}:
        if len(spec['containers']) != 1:
            raise WrongFormatError('')
        podInfo = {}
        ports = []
        name = ''
        if 'hostname' in spec:
            name = spec['hostname']
        else:
            name = hashlib.sha256(contentStr.encode('utf-8')).hexdigest()
        if 'labels' in metadata:
            podInfo['labels'] = metadata['labels']
        else:
            podInfo['labels'] = {}
        podInfo['image'] = spec['containers'][0]['image']
        for port in spec['containers'][0]['ports']:
            if 'name' in port:
                portName = port['name']
            else:
                portName = ''
            ports.append({'name': portName, 'number': port['containerPort']})
        podInfo['ports'] = ports
        return {'type': 'pod', 'name': name, 'info': podInfo}

    @classmethod
    def _parseService(cls, metadata: dict, spec: dict) -> {}:
        namespace = 'default'
        name = ''
        svcInfo = {}
        svcPorts = []
        if 'namespace' in metadata:
            namespace = metadata['namespace']
        #Suppose for now that is impossibile for services to use generateName
        name = metadata['name'] + '.' + namespace + '.svc'
        if 'selector' in spec:
            svcInfo['selector'] = spec['selector']
        else:
            svcInfo['selector'] = {}
        for svcPort in spec['ports']:
            portInfo = {}
            if 'name' in svcPort:
                portInfo['name'] = svcPort['name']
            else:
                portInfo['name'] = ''
            if 'nodePort' in svcPort:
                portInfo['nodePort'] = svcPort['nodePort']
            portInfo['port'] = svcPort['port']
            if 'targetPort' in svcPort:
                portInfo['targetPort'] = svcPort['targetPort']
            else:
                portInfo['targetPort'] = portInfo['port']
            svcPorts.append(portInfo)
        svcInfo['ports'] = svcPorts
        if 'type' in spec:
            svcInfo['type'] = spec['type']
        else:
            svcInfo['type'] = 'ClusterIP'
        return {'type': 'service', 'name': name, 'info': svcInfo}

    @classmethod
    def _parseEndpoints(cls, metadata: dict, spec: dict) -> {}:
        endpoints = []
        for subset in spec['subsets']:
            for address in subset['addresses']:
                ports = []
                for port in subset['ports']:
                    if 'name' in port:
                        portName = port['name']
                    else:
                        portName = ''
                    ports.append({'name': portName, 'number': port['port']})
                endpoints.append({'type': 'endpoint', 'name': address['hostname'], 'ip': address['ip'], 'ports': ports})
        return {'type': 'endpoints', 'info': endpoints}