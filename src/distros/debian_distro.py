from distros.generic_distro import GenericDistro


class DebianDistro(GenericDistro):

    def update(self, verbose, brew):
        super().update(verbose, brew)
