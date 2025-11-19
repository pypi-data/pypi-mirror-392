project(cpe-search)

SET(CMAKE_CXX_STANDARD 14)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include Json C++ file
include_directories(json/single_include)

ADD_EXECUTABLE(find_cpes find_cpes.cpp)

#if (NOT APPLE)
#    TARGET_LINK_LIBRARIES(create_db dl)
#endif()
