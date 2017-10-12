TEMPLATE = '''/* *** THIS FILE IS GENERATED - DO NOT EDIT! ***
 * See mock_icd_generator.py for modifications
 *
 * Copyright (c) 2017 LunarG, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * Copyright (c) 2015-2017 Valve Corporation
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Author: Mike Schuchardt <mikes@lunarg.com>
 */

@macro ifdef(guard)
@if guard
#ifdef {{guard}}
@endif
{{-caller()-}}
@if guard
#endif
@endif
@endmacro

#include <algorithm>
#include <cstring>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "vulkan/vk_icd.h"

static void* CreateHandle() {
    auto handle = new VK_LOADER_DATA;
    set_loader_magic_value(handle);
    return handle;
}

static void DestroyHandle(void* handle) {
    delete reinterpret_cast<VK_LOADER_DATA*>(handle);
}

// Callback function pointers
@for cmd in cmds
@call ifdef(cmd.guard)
static VKAPI_ATTR {{cmd.r_type}} (VKAPI_PTR *CALLBACK_{{cmd.base_name}})(void*, {{cmd.param_decls}}) = nullptr;
@endcall
@endfor

// Callback data pointers
@for cmd in cmds
@call ifdef(cmd.guard)
static void* DATA_{{cmd.base_name}} = nullptr;
@endcall
@endfor

// Entry point for setting callback functions and data
static VKAPI_ATTR void VKAPI_CALL SetProcAddr(const char* pName, PFN_vkVoidFunction pCallback, void* pData) {
    static const std::unordered_map<std::string, std::pair<PFN_vkVoidFunction*, void**>> callback_table = {
    @for cmd in cmds
    @call ifdef(cmd.guard)
        { "{{cmd.name}}", { (PFN_vkVoidFunction*)&CALLBACK_{{cmd.base_name}}, &DATA_{{cmd.base_name}} } },
    @endcall
    @endfor
    };
    const auto &item = callback_table.find(pName);
    if (item != callback_table.end()) {
        *(item->second).first = pCallback;
        *(item->second).second = pData;
    }
}

@for cmd in cmds
@if 'VKAPI_CALL COMMAND_' + cmd.base_name not in TEMPLATE
@call ifdef(cmd.guard)
static VKAPI_ATTR {{cmd.r_type}} VKAPI_CALL COMMAND_{{cmd.base_name}} ({{cmd.param_decls}}) {

    @for z_name, z_type in cmd.z_list
    if ({{z_name}}) memset({{z_name}}, 0, sizeof({{z_type}}));
    @endfor

    @if cmd.h_create
    @if cmd.h_count
    for (uint32_t i = 0; i < {{cmd.h_count}}; i++) {
        {{cmd.h_name}}[i] = ({{cmd.h_type}})CreateHandle();
    }
    @else
    *{{cmd.h_name}} = ({{cmd.h_type}})CreateHandle();
    @endif
    @endif

    @if cmd.h_destroy
    @if cmd.h_count
    for (uint32_t i = 0; i < {{cmd.h_count}}; i++) {
        DestroyHandle({{cmd.h_name}}[i]);
    }
    @else
    DestroyHandle({{cmd.h_name}});
    @endif
    @endif

    if (CALLBACK_{{cmd.base_name}}) return CALLBACK_{{cmd.base_name}}(DATA_{{cmd.base_name}}, {{cmd.param_names}});
    return{{' ' + cmd.r_value if cmd.r_value else ''}};
}
@endcall
{##}
@endif
@endfor

static VKAPI_ATTR VkResult VKAPI_CALL COMMAND_EnumeratePhysicalDevices (VkInstance instance, uint32_t* pPhysicalDeviceCount, VkPhysicalDevice* pPhysicalDevices) {
    static VkPhysicalDevice physical_device = (VkPhysicalDevice)CreateHandle();
    if (pPhysicalDevices) {
        *pPhysicalDevices = physical_device;
    } else {
        *pPhysicalDeviceCount = 1;
    }
    return VK_SUCCESS;
}

static VKAPI_ATTR void VKAPI_CALL COMMAND_GetDeviceQueue (VkDevice device, uint32_t queueFamilyIndex, uint32_t queueIndex, VkQueue* pQueue) {
    static std::unordered_map<VkDevice, std::unordered_map<uint32_t, std::unordered_map<uint32_t, VkQueue>>> queue_map;
    auto queue = queue_map[device][queueFamilyIndex][queueIndex];
    if (queue) {
        *pQueue = queue;
    } else {
        *pQueue = queue_map[device][queueFamilyIndex][queueIndex] = (VkQueue)CreateHandle();
    }

    if (CALLBACK_GetDeviceQueue) return CALLBACK_GetDeviceQueue(DATA_GetDeviceQueue, device, queueFamilyIndex, queueIndex, pQueue);
    return;
}

// dev sim doesn't hook this yet
static VKAPI_ATTR void VKAPI_CALL COMMAND_GetPhysicalDeviceFormatProperties (VkPhysicalDevice physicalDevice, VkFormat format, VkFormatProperties* pFormatProperties) {
    VkFormatProperties format_properties = { 0x00FFFFFF, 0x00FFFFFF, 0x00FFFFFF };
    if (CALLBACK_GetPhysicalDeviceFormatProperties) return CALLBACK_GetPhysicalDeviceFormatProperties(DATA_GetPhysicalDeviceFormatProperties, physicalDevice, format, pFormatProperties);
    return;
}

static VKAPI_ATTR VkResult VKAPI_CALL COMMAND_EnumerateInstanceExtensionProperties (const char* pLayerName, uint32_t* pPropertyCount, VkExtensionProperties* pProperties) {
    static const VkExtensionProperties properties[] = {
    @for ext in exts|selectattr('type', 'equalto', 'instance')
    @call ifdef(ext.guard)
        { "{{ext.name}}", {{ext.version}} },
    @endcall
    @endfor
    };
    static const uint32_t propertyCount = sizeof(properties) / sizeof(properties[0]);
    if (pProperties == nullptr) {
        *pPropertyCount = propertyCount;
    } else {
        for (uint32_t i = 0; i < *pPropertyCount && i < propertyCount; i++) {
            pProperties[i] = properties[i];
        }
    }

    return VK_SUCCESS;
}

static VKAPI_ATTR VkResult VKAPI_CALL COMMAND_EnumerateDeviceExtensionProperties (VkPhysicalDevice physicalDevice, const char* pLayerName, uint32_t* pPropertyCount, VkExtensionProperties* pProperties) {
    const VkExtensionProperties properties[] = {
    @for ext in exts|selectattr('type', 'equalto', 'device')
    @call ifdef(ext.guard)
        { "{{ext.name}}", {{ext.version}} },
    @endcall
    @endfor
    };
    static const uint32_t propertyCount = sizeof(properties) / sizeof(properties[0]);
    if (pProperties == nullptr) {
        *pPropertyCount = propertyCount;
    } else {
        for (uint32_t i = 0; i < *pPropertyCount && i < propertyCount; i++) {
            pProperties[i] = properties[i];
        }
    }

    return VK_SUCCESS;
}

static VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL COMMAND_GetDeviceProcAddr (VkDevice device, const char* pName);

static VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL COMMAND_GetInstanceProcAddr (VkInstance instance, const char* pName) {
    static const std::unordered_map<std::string, PFN_vkVoidFunction> function_table = {
    @for cmd in cmds
    @call ifdef(cmd.guard)
        { "{{cmd.name}}", (PFN_vkVoidFunction)COMMAND_{{cmd.base_name}} },
    @endcall
    @endfor
        { "vkSetProcAddr", (PFN_vkVoidFunction)SetProcAddr },
    };
    const auto &item = function_table.find(pName);
    if (item != function_table.end()) {
        return item->second;
    }
    return nullptr;
}

static VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL COMMAND_GetDeviceProcAddr (VkDevice device, const char* pName) {
    return COMMAND_GetInstanceProcAddr(nullptr, pName);
}


#ifdef WIN32
    #define EXPORT extern "C" __declspec(dllexport)
#else
    #define EXPORT extern "C"
#endif
EXPORT VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL vk_icdGetInstanceProcAddr(VkInstance instance, const char* pName) {
    return COMMAND_GetInstanceProcAddr(instance, pName);
}

'''

import os,re,sys,string
import xml.etree.ElementTree as etree
import jinja2
from collections import namedtuple

class CmdInfo:
    def __init__(self, cmd_elem, root):
        self.name = cmd_elem.find('proto').find('name').text
        self.base_name = self.name[2:]
        try:
            self.guard = root.find('extensions/extension/require/command[@name="{}"]/../..'.format(self.name)).attrib['protect']
        except:
            self.guard = None

        self.param_decls = ', '.join([''.join(p.itertext()) for p in cmd_elem.findall('param')])
        self.param_names = ', '.join([p.find('name').text for p in cmd_elem.findall('param')])

        self.r_type = cmd_elem.find('proto').find('type').text
        self.r_value = {'void':               '',
                        'VkResult':           'VK_SUCCESS',
                        'VkBool32':           'VK_TRUE',
                        'PFN_vkVoidFunction': 'nullptr'}[self.r_type]

        first_word = re.search('[A-Z][a-z]+', self.name).group()
        if first_word in ('Create', 'Allocate'):
            self.h_create = True
            param = cmd_elem.findall('param')[-1]
            self.h_name = param.find('name').text
            self.h_type = param.find('type').text
            if 'len' in param.attrib:
                self.h_count = param.attrib['len'].replace('::', '->')

        elif first_word in ('Destroy', 'Free'):
            self.h_destroy = True
            h_idx = -2 if 'pAllocator' in [e.text for e in cmd_elem.findall('param/name')] else -1
            param = cmd_elem.findall('param')[h_idx]
            self.h_name = param.find('name').text
            self.h_type = param.find('type').text
            if 'len' in param.attrib:
                self.h_count = param.attrib['len'].replace('::', '->')

        else:
            self.z_list = []
            for param in cmd_elem.findall('param'):
                param_decl = ''.join(param.itertext())
                param_name = param.find('name').text
                param_type = param.find('type').text
                type_blacklist = ('void', 'xcb_connection_t')
                if '*' in param_decl and 'const' not in param_decl and param_type not in type_blacklist:
                    self.z_list.append((param_name, param_type))
             



class ExtInfo:
    def __init__(self, ext_elem):
        self.name = ext_elem.attrib['name']
        self.supported = ext_elem.attrib['supported']
        self.type = ext_elem.attrib['type']
        for enum_elem in ext_elem.findall('require/enum'):
            if enum_elem.attrib['name'].endswith('_VERSION'):
                self.version = enum_elem.attrib['value']
        try:
            self.guard = ext_elem.attrib['protect']
        except:
            self.guard = None

if __name__ == '__main__':
    root = etree.parse(sys.argv[1]).getroot()
    cmds = [CmdInfo(e, root) for e in root.findall('commands/command')]
    exts = [ExtInfo(e) for e in root.findall('extensions/extension[@supported="vulkan"]')]
    template = jinja2.Template(TEMPLATE, line_statement_prefix='@')
    with open('mock_icd.cpp', 'w') as out_file:
        out_file.write(template.render(locals()))
        

