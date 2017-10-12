cmake_minimum_required(VERSION 3.0)

project (MockICD)

find_package(PythonInterp 3 REQUIRED)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../LVL/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_library(mock_icd SHARED mock_icd.cpp)

add_custom_command(
    OUTPUT mock_icd.cpp
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/mock_icd_generator.py ${CMAKE_CURRENT_SOURCE_DIR}/../LVL/scripts/vk.xml
    DEPENDS mock_icd_generator.py
    )

if(WIN32)
	add_definitions(-DVK_USE_PLATFORM_WIN32_KHR)
    add_custom_command(TARGET mock_icd POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${CMAKE_CURRENT_SOURCE_DIR}/mock_icd_windows.json"
        "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIGURATION>/mock_icd.json"
        )
else()
    add_definitions(-DVK_USE_PLATFORM_XCB_KHR)
    add_custom_command(TARGET mock_icd POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${CMAKE_CURRENT_SOURCE_DIR}/mock_icd_linux.json"
        "${CMAKE_CURRENT_BINARY_DIR}/mock_icd.json"
        )
endif()
