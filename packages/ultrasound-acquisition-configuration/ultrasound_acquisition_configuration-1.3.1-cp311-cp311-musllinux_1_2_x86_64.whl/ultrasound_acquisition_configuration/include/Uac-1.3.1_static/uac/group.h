#pragma once

#include <algorithm>

#include <urx/group.h>

#include <uac/event.h>
#include <uac/igroup.h>

namespace uac {

struct Group : urx::detail::Group<Event>, IGroup {
  bool operator==(const IGroup& other) const override {
    const Group* pointer = dynamic_cast<const Group*>(&other);
    return pointer != nullptr && urx::detail::Group<Event>::operator==(*pointer) &&
           IGroup::operator==(other);
  }

  bool operator!=(const Group& other) const { return !operator==(other); }
};

}  // namespace uac
