cmake_minimum_required(VERSION 3.27)

project(clak)

include(FetchContent)
FetchContent_Declare(lexy URL https://lexy.foonathan.net/download/lexy-src.zip)
FetchContent_MakeAvailable(lexy)

add_executable(clak)
target_sources(clak PRIVATE clak.cpp)
target_link_libraries(clak PRIVATE foonathan::lexy)