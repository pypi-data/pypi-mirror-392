#pragma once

#include <memory>
#include <string>
#include <utility>

#include <urx/detail/compare.h>

#include <uac/igroup.h>

namespace uac {

struct SuperGroup : IGroup {
  bool operator==(const IGroup& other) const override {
    const SuperGroup* pointer = dynamic_cast<const SuperGroup*>(&other);
    return pointer != nullptr && IGroup::operator==(other) &&
           urx::valueComparison(initial_group, pointer->initial_group) &&
           description == pointer->description;
  }

  bool operator!=(const SuperGroup& other) const { return !operator==(other); }

  std::weak_ptr<IGroup> initial_group;
  std::string description;
};

}  // namespace uac
