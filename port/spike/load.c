// Phase 1 spike: dlopen FM27's game_plugin in our own process (route A).
// Reads the installed bundle in place; never modifies it.
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : getenv("FM27_GAME_PLUGIN");
    if (!path) { fprintf(stderr, "usage: load <path to game_plugin>\n"); return 2; }
    fprintf(stderr, "[spike] arch=%s SteamAppId=%s\n",
#if defined(__x86_64__)
            "x86_64",
#else
            "arm64",
#endif
            getenv("SteamAppId") ? getenv("SteamAppId") : "(unset)");
    void *h = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!h) { fprintf(stderr, "[spike] dlopen FAILED: %s\n", dlerror()); return 1; }
    for (uint32_t i = 0; i < _dyld_image_count(); i++) {
        const char *n = _dyld_get_image_name(i);
        if (strstr(n, "game_plugin.bundle")) {
            const struct mach_header_64 *mh = (const void *)_dyld_get_image_header(i);
            fprintf(stderr, "[spike] OK image#%u base=%p slide=0x%lx cputype=0x%x\n", i, (void *)mh,
                    (long)_dyld_get_image_vmaddr_slide(i), mh->cputype);
        }
    }
    fprintf(stderr, "[spike] loaded images=%u; exiting without calling engine code\n", _dyld_image_count());
    return 0;
}
