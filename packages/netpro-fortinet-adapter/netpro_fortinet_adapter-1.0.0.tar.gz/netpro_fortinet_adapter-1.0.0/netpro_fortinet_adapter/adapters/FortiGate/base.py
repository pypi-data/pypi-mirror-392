import sys
import requests
import datetime
from netpro.utils.exceptions import APIError
from netpro.utils.validators import validate_IPv4Address
from netpro.adapters.base.api import APIAdapterBase
from netpro.adapters.utils import inventory
from .serializers import base


__all__ = (
    'BaseFortigateAPIAdapter',
)



class BaseFortigateAPIAdapter(APIAdapterBase):
    """
    Base Fortigate API Adapter. Based on FortiOS v7.6
    """ 
    inventory_domain = "firewall"
    
    PolicyLookupSerializer = base.PolicyLookupSerializer
    
    def __init__(self, data=None, logger_name='FORTIGATE', debug=False, **kwargs):
        super().__init__(logger_name=logger_name, **kwargs)
        self.hostname = None
        self.vdom = 'root'
        self.version = ''
        self.interfaces = {}
        self.zones = {}
        self.addresses = {}
        self.address_groups = {}
        self.services = {}
        self.service_groups = {}
        self.security_profiles = []
        # self.profile_groups = {}
        self.ippools = {}
        self.ipv4_routes = {}
        self.ipv6_routes = {}
        self.policies = {}
        self.routing_policies = {}
        self.vdoms = []
        self.schedule_onetime = {}
        self.schedule_recurring = {}
        self.schedule_groups = {}
        self.users = {}
        self.user_groups = {}
        self.authentication_servers = {}
        self.vip = {}
        self.vip_groups = {}
        self.system_info = {}
        self.profile_types = {
            'sec_profilegroup': {
                'key': 'profile-group',
                'uri': '/cmdb/firewall/profile-group/'
            },
            'sec_protocol': {
                'key': 'profile-protocol-options',
                'uri': '/cmdb/firewall/profile-protocol-options/'
            },
            'sec_antivirus': {
                'key': 'av-profile',
                'uri': '/cmdb/antivirus/profile/'
            },
            'sec_web': {
                'key': 'webfilter-profile',
                'uri': '/cmdb/webfilter/profile/'
            },
            'sec_video': {
                'key': 'videofilter-profile',
                'uri': '/cmdb/videofilter/profile/'
            },
            'sec_dns': {
                'key': 'dnsfilter-profile',
                'uri': '/cmdb/dnsfilter/profile/'
            },
            'sec_app': {
                'key': 'application-list',
                'uri': '/cmdb/application/list/'
            },
            'sec_ips': {
                'key': 'ips-sensor',
                'uri': '/cmdb/ips/sensor/'
            },
            'sec_voip': {
                'key': 'voip-profile',
                'uri': '/cmdb/voip/profile/'
            },
            'sec_ssl': {
                'key': 'ssl-ssh-profile',
                'uri': '/cmdb/firewall/ssl-ssh-profile/',
            },
            'sec_file': {
                'key': 'file-filter-profile',
                'uri': '/cmdb/file-filter/profile/'
            },
            'sec_email': {
                'key': 'emailfilter-profile',
                'uri': '/cmdb/emailfilter/profile/'
            },
            'sec_waf': {
                'key': 'waf-profile',
                'uri': '/cmdb/waf/profile/'
            }
        }

        if data:
            self.vdom = data.get('vdom', self.vdom) or self.vdom
            status = self.set_data(data)
            if not status[0]:
                raise APIError(status[1])

    def _build_login_url(self, ip=None):
        return f"https://{ip or self.ip}:{self.port}/logincheck"

    def _build_login_payload(self):
        return f"username={self.user}&secretkey={self.password}"
    
    def _get_keepalive_url(self):
        return f"https://{self.ip}:{self.port}/api/v2/monitor/system/status"
    
    def _build_url(self, path: str) -> str:
        return f"https://{self.ip}:{self.port}/api/v2/{path.strip('/')}?vdom={self.vdom}"
    
    def _validate_session(self):
        # FortiGate specific session check
        try:
            status = self.get_system_info()
            if not status[0]:
                raise APIError(status[1])
            return [True, "Session validated"]
        except requests.RequestException as e:
            return [False, f"Session validation request failed: {e}"]
        except Exception as e:
            return [False, f"Unexpected error in session validation: {e}"]
        
    @inventory('system_info')
    def get_system_info(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url(f'monitor/system/status')
            headers = {'Content-Type': 'application/json'}
            response = self.session.get(url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()
            vdom = data.get('vdom', '')
            if self.vdom and vdom != self.vdom:
                self.logger.warning(f'Mismatched vdom. Expected: {self.vdom}, Got: {vdom}')
                self.vdom = vdom
            
            self.hostname = data.get('results', {}).get('hostname', self.hostname)
            self.version = data.get('version')
            self.system_info = {
                'name': self.hostname,
                'vdc': self.vdom,
                'os_version': self.version,
                'serial': data.get('serial')
            }
            output = [True, self.system_info]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output  
    
    def get_vdoms(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url(f'cmdb/system/vdom')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            self.vdoms = [item['name'] for item in status[1]]
            output = [True, self.vdoms]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    @inventory('interfaces')
    def get_interfaces(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('cmdb/system/interface')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            interfaces = {
                'Null': {
                    'name': 'Null',
                    'ip_address': '',
                    'status': 'up',
                    'type': 'null',
                    'description': 'Added by the system',
                    'vdc': self.vdom,
                    'enabled': True,
                    'parent': '',
                    'comments': '**DO NOT DELETE**. This is used for routing'
                },
                'any': {
                    'name': 'any',
                    'ip_address': '',
                    'status': 'up',
                    'type': 'any',
                    'description': 'Added by the system',
                    'vdc': self.vdom,
                    'enabled': True,
                    'parent': '',
                    'comments': '**DO NOT DELETE**. This is used for DNAT'
                },
                self.vdom: {
                    'name': self.vdom,
                    'ip_address': '',
                    'status': 'up',
                    'type': 'vdom',
                    'description': 'Added by the system',
                    'vdc': self.vdom,
                    'enabled': True,
                    'parent': '',
                    'comments': '**DO NOT DELETE**. This is used for routing'
                }
            }
            interfaces_with_parent = {}

            interface_with_errors = []
            for item in status[1]:
                if item['type'] in ['vdom-link']:
                    msg = f'Skipping {item["type"]} type interface ({item["name"]})'
                    self.logger.info(msg)
                    interface_with_errors.append([item['name'], msg])
                    continue
                if item['vdom'] == self.vdom:
                    status = validate_IPv4Address(item['ip'])
                    if not status[0]:
                        self.logger.info(status[1])
                        self.logger.error(f'Unable to add interface "{item["name"]}" due to {status[1]}')
                        self.logger.debug(f'data: \n{item}')
                        interface_with_errors.append([item['name'], status[1]])
                        continue
                    ip = status[1]
                    parent = item['interface'] if item['type'] == 'tunnel' and item['interface'] else item.get('aggregate', None)
                    interface = {
                        'name': item['name'],
                        'ip_address': '' if '0.0.0.0' in ip else ip,
                        'status': item['status'],
                        'type': item['type'],
                        # 'member': [i['interface-name'] for i in item['member']] if item['member'] else [],
                        'comments': item.get('description', ''),
                        'description': item.get('alias', ''),
                        # 'role': None if item['role'] == 'undefined' else item['role'],
                        'vdc': item.get('vdom', ''),
                        'enabled': True if item['status'] == 'up' else False,
                        'parent': parent
                    }
                    if parent:
                        interfaces_with_parent[item['name']] = interface
                    else:
                        interfaces[item['name']] = interface
            self.interfaces = {**interfaces, **interfaces_with_parent}
            output = [True, interfaces, interface_with_errors]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    @inventory('zones')
    def get_zones(self, zone=''):
        output = [False, 'Unknown']
        try:
            url = self._build_url(f'cmdb/system/zone/{zone}')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            zones = {}
            for item in status[1]:
                zones[item['name']] = {
                    'name': item['name'],
                    'intrazone': item['intrazone'],
                    'type': 'zone',
                    'members': [i['interface-name'] for i in item['interface']] if item['interface'] else []
                }
            if not zone:
                self.zones = zones
                self.get_sdwan_zones()
            else:
                zones = zones[zone]
            output = [True, zones]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output

    def get_sdwan_zones(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url(f'cmdb/system/sdwan')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            zones = {}
            for item in status[1]['zone']:
                zones[item['name']] = {
                    'name': item['name'],
                    'intrazone': item.get('intrazone', 'deny'),
                    'type': 'sdwan',
                    'members': []
                }
            for item in status[1]['members']:
                if item['interface'] not in zones[item['zone']]['members']:
                    zones[item['zone']]['members'].append(item['interface'])
            
            self.zones.update(zones)
            output = [True, self.zones]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output

    @inventory('addresses')
    def get_address_objects(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall/address/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                if item['type'] == 'interface-subnet':
                    item['type'] = 'ipmask'
                # if item['type'] == 'dynamic' and item['sub-type'] == 'ems-tag':
                #     item['type'] = 'tag'
                if item['type'] not in ['ipmask', 'iprange', 'fqdn', 'mac', 'geography', 'tag']:
                    continue
                macaddress = []
                for i in item['macaddr']: macaddress.append(i['macaddr'])
                if item['type'] == 'mac' and not macaddress:
                    continue
                objects[item['name']] = {
                    'name': item['name'],
                    'type': item['type'],
                    'subnet': validate_IPv4Address(item['subnet'])[1] if 'subnet' in item else '',
                    'start_ip': item.get('start-ip', ''),
                    'end_ip': item.get('end-ip', ''),
                    'fqdn': item.get('fqdn', ''),
                    'country': item.get('country', ''),
                    'tag': item.get('obj-tag', ''),
                    'mac': [i['macaddr'] for i in item['macaddr']] if 'macaddr' in item and item['macaddr'] else [],
                    'comments': item['comment'],
                }
            self.addresses = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output

    @inventory('address_groups')
    def get_address_groups(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall/addrgrp/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            object = {}
            addrgrp_names = [i['name'] for i in status[1]]
            addrgrp = {}
            addrgrp_with_addrgrp = {}
            for item in status[1]:
                has_addrgrp = False
                members = []
                for member in item['member']:
                    if member['name'] in addrgrp_names:
                        has_addrgrp = True
                    members.append(member['name'])

                object = {
                    'name': item['name'],
                    # 'type': item['type'],
                    'members': members,
                    'comments': item['comment'],
                }

                if has_addrgrp:
                    addrgrp_with_addrgrp[item['name']] = object
                else:
                    addrgrp[item['name']] = object

            self.address_groups = {**addrgrp, **addrgrp_with_addrgrp}
            output = [True, self.address_groups]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
        
    @inventory('services')
    def get_services(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall.service/custom/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                icmpcode = item.get('icmpcode', None)
                icmptype = item.get('icmptype', None)
                tcp_port = item.get('tcp-portrange', '')
                udp_port = item.get('udp-portrange', '')
                if item['protocol'].lower() in ['tcp/udp/udp-lite/sctp', 'tcp/udp/sctp']:
                    if tcp_port and udp_port:
                        protocol = 'tcp/udp'
                    elif tcp_port:
                        protocol = 'tcp'
                    elif udp_port:
                        protocol = 'udp'
                else:
                    protocol = item['protocol'].lower()

                objects[item['name']] = {
                    'name': item['name'],
                    'protocol': protocol,
                    'protocol_number': item.get('protocol-number', None),
                    'icmptype': None if icmptype == '' else icmptype,
                    'icmpcode': None if icmpcode == '' else icmpcode,
                    'tcp_port': tcp_port,
                    'udp_port': udp_port, 
                    'comments': item['comment'],
                }

            self.services = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output

    @inventory('service_groups')
    def get_service_groups(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall.service/group/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            object = {}
            servicegroup_names = [i['name'] for i in status[1]]
            servicegroup = {}
            servicegroup_with_servicegroup = {}
            for item in status[1]:
                has_servicegroup = False
                members = []
                for member in item['member']:
                    if member['name'] in servicegroup_names:
                        has_servicegroup = True
                    members.append(member['name'])

                object = {
                    'name': item['name'],
                    'members': members,
                    'comments': item['comment'],
                }

                if has_servicegroup:
                    servicegroup_with_servicegroup[item['name']] = object
                else:
                    servicegroup[item['name']] = object

            self.service_groups = {**servicegroup, **servicegroup_with_servicegroup}
            output = [True, self.service_groups]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
        
    @inventory('schedule_onetime')
    def get_schedule_onetime(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall.schedule/onetime/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                objects[item['name']] = {
                    'name': item['name'],
                    'start': item['start'],
                    'end': item['end']
                }
            self.schedule_onetime = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
        
    @inventory('schedule_recurring')
    def get_schedule_recurring(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall.schedule/recurring/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                objects[item['name']] = {
                    'name': item['name'],
                    'start': item['start'],
                    'end': item['end'],
                    'day': item['day']
                }
            self.schedule_recurring = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
        
    @inventory('schedule_groups')
    def get_schedule_groups(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall.schedule/group/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            object = {}
            schedulegroup_names = [i['name'] for i in status[1]]
            schedulegroup = {}
            schedulegroup_with_schedulegroup = {}
            for item in status[1]:
                has_schedulegroup = False
                members = []
                for member in item['member']:
                    if member['name'] in schedulegroup_names:
                        has_schedulegroup = True
                    members.append(member['name'])

                object = {
                    'name': item['name'],
                    'members': members,
                }

                if has_schedulegroup:
                    schedulegroup_with_schedulegroup[item['name']] = object
                else:
                    schedulegroup[item['name']] = object

            self.schedule_groups = {**schedulegroup, **schedulegroup_with_schedulegroup}
            output = [True, self.schedule_groups]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
        
    @inventory('security_profiles')
    def get_security_profiles(self):
        output = [False, 'Unknown']
        try:
            objects = []
            for type, profile in self.profile_types.items():
                url = self._build_url(profile['uri'])
                status = self.api_request(url)
                if not status[0]:
                    raise APIError(status[1])
                for item in status[1]:
                    objects.append({
                        'name': item['name'],
                        'description': item.get('comment', ''),
                        'type': type
                    })
            self.security_profiles = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
        
    # @inventory('profile_groups')
    # def get_profile_groups(self):
    #     output = [False, 'Unknown']
    #     try:
    #         url = self._build_url('/cmdb/firewall/profile-group/')
    #         status = self.api_request(url)
    #         if not status[0]:
    #             raise APIError(status[1])
    #         objects = {}
    #         for item in status[1]:
    #             profiles = [{'name': item.get(i['key']), 'type': k} for k, i in self.profile_types.items() if item.get(i['key'], '')]
    #             objects[item['name']] = {
    #                 'name': item['name'],
    #                 'description': item['comment'],
    #                 'profiles': profiles
    #             }
    #         self.profile_groups = objects
    #         output = [True, objects]
    #     except APIError as err:
    #         self.logger.error(err)
    #         output = [False, str(err)]
    #     except:
    #         exc_type, exc_value, exc_tb = sys.exc_info()
    #         err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
    #         self.logger.exception(err)
    #         output = [False, err]
    #     finally:
    #         return output
    
    # @inventory('ippools')
    # def get_ippools(self):
    #     output = [False, 'Unknown']
    #     try:
    #         url = self._build_url('/cmdb/firewall/ippool/')
    #         status = self.api_request(url)
    #         if not status[0]:
    #             raise APIError(status[1])
    #         objects = {}
    #         for item in status[1]:
    #             objects[item['name']] = {
    #                 'name': item['name'],
    #                 'type': item['type'],
    #                 'startip': item['startip'],
    #                 'endip': item['endip'],
    #                 'startport': item['startport'],
    #                 'endport': item['endport'],
    #                 'source_startip': item['source-startip'],
    #                 'source_endip': item['source-endip'],
    #                 # 'block_size': item['block-size'],
    #                 # 'num_blocks_per_user': item['num-blocks-per-user'],
    #                 # 'arp_reply': item['arp-reply'],
    #                 'comments': item['comments'],
    #             }
    #         self.ippools = objects
    #         output = [True, objects]
    #     except APIError as err:
    #         self.logger.error(err)
    #         output = [False, str(err)]
    #     except:
    #         exc_type, exc_value, exc_tb = sys.exc_info()
    #         err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
    #         self.logger.exception(err)
    #         output = [False, err]
    #     finally:
    #         return output
        
    @inventory('users')
    def get_users(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/user/local/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                if item['ldap-server']:
                    server = item['ldap-server']
                elif item['radius-server']:
                    server = item['radius-server']
                elif item['tacacs+-server']:
                    server = item['tacacs+-server']
                else:
                    server = ''
                objects[item['name']] = {
                    'name': item['name'],
                    'type': 'local_user' if item['type'] == 'password' else f"{item['type']}_user",
                    'status': item['status'],
                    'server': server
                }
            self.users = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    @inventory('user_groups')
    def get_user_groups(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/user/group/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                objects[item['name']] = {
                    'name': item['name'],
                    'members': [i['name'] for i in item['member']] if item['member'] else [],
                    # 'match': [{'server_name': i['server-name'], 'group_name': i['group-name']} for i in item['match']] if item['match'] else {}
                }
            self.user_groups = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    @inventory('vip')
    def get_vip(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall/vip/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                objects[item['name']] = {
                    'name': item['name'],
                    'type': item['type'],
                    'source_filter': [i['range'] for i in item['src-filter']] if item['src-filter'] else [],
                    'service': [i['name'] for i in item['service']] if item['service'] else [],
                    'external_ip': item['extip'],
                    'external_address': item['extaddr'][0]['name'] if item['extaddr'] else '',
                    'mapped_ip': item['mappedip'][0]['range'] if item['mappedip'] else '',
                    'mapped_address': item['mapped-addr'],
                    'external_interface': item['extintf'],
                    'port_forward': item['portforward'],
                    'status': item['status'],
                    'protocol': item['protocol'],
                    'external_port': item['extport'],
                    'mapped_port': item['mappedport'],
                    'portmapping_type': item['portmapping-type'],
                    'comments': item['comment'],
                }
            self.vip = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    @inventory('vip_groups')
    def get_vip_groups(self):
        output = [False, 'Unknown']
        try:
            url = self._build_url('/cmdb/firewall/vipgrp/')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            objects = {}
            for item in status[1]:
                objects[item['name']] = {
                    'name': item['name'],
                    'interface': item['interface'],
                    'members': [i['name'] for i in item['member']] if item['member'] else [],
                    'comments': item['comments']
                }
            self.vip_groups = objects
            output = [True, objects]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    @inventory('authentication_servers')
    def get_authentication_servers(self):
        output = [False, 'Unknown']
        types = ['radius', 'tacacs+', 'ldap', 'saml']
        try:
            for type in types:
                url = self._build_url(f'/cmdb/user/{type}/')
                status = self.api_request(url)
                if not status[0]:
                    raise APIError(status[1])
                objects = {}
                for item in status[1]:
                    objects[item['name']] = {
                        'name': item['name'],
                        'type': type,
                        'server': item.get('server', '')
                    }
                self.authentication_servers.update(objects)
            output = [True, self.authentication_servers]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    @inventory('policies')
    def get_policies(self, policy=''):
        output = [False, 'Unknown']
        try:
            url = self._build_url(f'cmdb/firewall/policy/{policy}')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            policies = {}
            position = 0
            for item in status[1]:
                # if item['name'] or policy:
                position = position + 1
                security_profile = {}
                for k, v in self.profile_types.items():
                    profile = item.get(v['key'], None)
                    if profile:
                        security_profile[k] = profile   

                    users = {}
                    if item['users']:
                        users['users'] = [i['name'] for i in item['users']]
                    if item['groups']:
                        users['groups'] = [i['name'] for i in item['groups']]

                policies[item['policyid']] = {
                    'policyid': item['policyid'],
                    'name': item['name'],
                    'status': item['status'],
                    'source_interface': [i['name'] for i in item['srcintf']] if item['srcintf'] else [],
                    'destination_interface': [i['name'] for i in item['dstintf']] if item['dstintf'] else [],
                    'action': 'allow' if item['action'] == 'accept' else item['action'],
                    'source_address': [i['name'] for i in item['srcaddr']] if item['srcaddr'] else [],
                    'destination_address': [i['name'] for i in item['dstaddr']] if item['dstaddr'] else [],
                    'schedule': item['schedule'],
                    'service': [i['name'] for i in item['service']] if item['service'] else [],
                    'inspection_mode': item['inspection-mode'],
                    'security_profile': security_profile,
                    'logging': item['logtraffic'],
                    'nat': item['nat'],
                    'users': users,
                    'expiry_date': datetime.datetime.strptime(
                        item['policy-expiry-date'], "%Y-%m-%d %H:%M:%S"
                    ).strftime("%H:%M %Y/%m/%d") if 'policy-expiry-date' in item and item['policy-expiry-date'] else None,
                    'comments': item['comments'],
                    'position': position
                }
                
            self.policies = policies
            if policy:
                policies = policies[policy]
            output = [True, policies]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
    
    def get_routing_table(self, version=4):
        output = [False, 'Unknown']
        try:
            if version != 4:
                raise APIError("IPv6 does not supported yet.")
            
            url = self._build_url(f'monitor/router/ipv{version}')
            status = self.api_request(url)
            if not status[0]:
                raise APIError(status[1])
            routes = {}
            for item in status[1]:
                route = {
                    'type': item['type'],
                    'gateway': '' if item['gateway'] == '0.0.0.0' or item['gateway'] == '::' else item['gateway'],
                    'interface': item['interface'],
                    'distance': item['distance'],
                    'priority': item['priority'],
                    'metric': item['metric'],
                }
                if 'is_tunnel_route' in item:
                    if item['is_tunnel_route']:
                        url = self._build_url(f"cmdb/system/interface/{item['interface']}")
                        status = self.api_request(url)
                        if not status[0]:
                            self.logger.warning(f'Unable to add {item['ip_mask']} due to {status[1]}')
                            continue
                        gw = status[1][0]['remote-ip'].split(' ')[0]
                        if gw != '0.0.0.0':
                            route['gateway'] = gw
                        else:
                            route['gateway'] = '' if item['gateway'] == '0.0.0.0' else item['gateway']

                if item['ip_mask'] not in routes:
                    routes[item['ip_mask']] = [route]
                else:
                    routes[item['ip_mask']].append(route)

            if version == 4:
                self.ipv4_routes = routes
            else:
                self.ipv6_routes = routes
            output = [True, routes]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output
        
    @inventory('ipv4_routes')
    def get_ipv4_routes(self):
        output = [False, 'Unknown']
        try:
            status = self.get_routing_table(version=4)
            if not status[0]:
                raise APIError(status[1])
            output = [True, status[1]]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        return output

        
    def policy_lookup(self, **kwargs):
        """
        Perform a firewall policy lookup on a FortiGate device.
        :param srcintf: Source interface
        :param src: Source IP
        :param dst: Destination IP
        :param protocol: Protocol number (default 1 = ICMP, 6 = TCP, 17 = UDP)
        :param destport: Destination port
        :param auth_type: Optional - 'user' or 'group'
        :param user_group: Optional - user or group name
        :param icmptype: Optional - ICMP type (e.g., 8 = echo request)
        :param username: Optional
        :return: [Bool: True, int: str: 'allow'|'deny', policy_id] or [False, str: error]
        """
        output = [False, 'Unknown']
        try:
            serializer = self.PolicyLookupSerializer(data=kwargs)
            if not serializer.is_valid():
                return [False, serializer.errors]

            params = serializer.validated_data

            ALLOWED_API_FIELDS = [
                'ipv6', 'srcintf', 'sourceip', 'dest', 'protocol',
                'destport', 'auth_type', 'user_group', 'icmptype'
            ]
            
            # Filter params: include only those keys that are allowed and have a value
            params = {k: v for k, v in params.items() if k in ALLOWED_API_FIELDS and v is not None}
            # if 'ipv6' in params:
            #     params['ipv6'] = str(params['ipv6']).lower()
        
            # Make API request
            url = self._build_url('monitor/firewall/policy-lookup')
            status = self.api_request(url, params=params)

            if not status[0]:
                raise APIError(status[1])
            response_data = status[1]

            # Validate response
            if not isinstance(response_data, dict):
                self.logger.debug(f'Invalid response format:\n{response_data}')
                raise APIError("Invalid response format")
            if "success" not in response_data:
                self.logger.debug(f'"success" key not found in response:\n{response_data}')
                raise APIError('"success" key not found in response.')

            if response_data["success"]:
                policy_id = response_data.get("policy_id", 0)
                if policy_id != 0 and 'policy_action' not in response_data:
                    # For older version below 7.4 which does not have "policy_action" key
                    if not self.policies:
                        status = self.get_policies(policy=policy_id)
                        if not status[0]:
                            raise APIError(status[1])
                        action = status[1]['action']
                    else:
                        action = self.policies[policy_id]['action']
                else:   
                    action = response_data.get("policy_action", "deny")
                action = 'allow' if action == 'accept' else action
                output = [True, action, policy_id]
            else:
                error_detail = response_data.get("error_code", str(response_data))
                output = [False, error_detail]
        except APIError as err:
            self.logger.error(err)
            output = [False, str(err)]
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            err = f"Unhandled Error [{exc_tb.tb_frame.f_code.co_name}:{exc_tb.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(err)
            output = [False, err]
        finally:
            self.close_session()
        return output
            