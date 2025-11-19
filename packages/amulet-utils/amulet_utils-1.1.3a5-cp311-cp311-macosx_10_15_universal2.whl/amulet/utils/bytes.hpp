#pragma once

#include <string>

namespace Amulet {

// A subclass of std::string to simplify casting to Python.
class Bytes : public std::string {
public:
    using std::string::string;
};

} // namespace Amulet
