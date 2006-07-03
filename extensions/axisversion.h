#ifndef EMC_VERSION_CHECK


#if defined(AXIS_USE_EMC2)
#define EMC_VERSION_MAJOR 2
#define EMC_VERSION_MINOR 0
#define EMC_VERSION_MICRO 0
#else
#define EMC_VERSION_MAJOR 1
#define EMC_VERSION_MINOR 0
#define EMC_VERSION_MICRO 0
#endif

#define EMC_VERSION_CHECK(major,minor,micro) \
    (EMC_VERSION_MAJOR > (major) || \
     (EMC_VERSION_MAJOR == (major) && EMC_VERSION_MINOR > (minor)) || \
     (EMC_VERSION_MAJOR == (major) && EMC_VERSION_MINOR == (minor) && \
      EMC_VERSION_MICRO >= (micro)))

#endif
