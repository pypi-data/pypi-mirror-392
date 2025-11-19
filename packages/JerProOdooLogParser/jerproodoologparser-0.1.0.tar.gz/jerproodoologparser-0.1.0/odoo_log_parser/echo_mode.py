# -*- coding: utf-8 -*-
from importlib.metadata import entry_points

class EchoMode:
    @classmethod
    def get_echo_plugin(self, mode):
        """
        Returna a function to convert a log digest into a string
        to be printed-out to the user.
            mode    The name of a mode.
        """
        if mode == 'python':
            return repr
        elif mode in EchoMode.get_echo_modes_list():
            matching_eps = [
                em
                for em in entry_points(group='odoo_log_parser.echo_modes')
                if em.name == mode
                ]
            return matching_eps[0].load()
        else:
            return None

    @classmethod
    def get_echo_modes_list(self):
        return [
            em.name
            for em in entry_points(group='odoo_log_parser.echo_modes')
            ]
