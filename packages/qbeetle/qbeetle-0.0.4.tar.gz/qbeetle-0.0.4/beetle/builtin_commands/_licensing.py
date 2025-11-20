
from beetle.translate import _
from beetle import path
from beetle.builtin_commands import prompt_for_value, require_project_existing
from beetle.builtin_commands._util import update_json
from beetle_runtime.project import PROJECTINFO
from beetle.cmdline import command

import json
import logging

_LOG = logging.getLogger(__name__)


@command
def init_licensing():
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    try:
        import rsa
    except ImportError:
        _LOG.error(
            'Please install Python library `rsa`. Eg. via:\n'
            '    pip install rsa'
        )
        return
    nbits = _prompt_for_nbits()
    print('')
    pubkey, privkey = rsa.newkeys(nbits)
    pubkey_args = {'n': pubkey.n, 'e': pubkey.e}
    privkey_args = {
        attr: getattr(privkey, attr) for attr in ('n', 'e', 'd', 'p', 'q')
    }
    update_json(path(PROJECTINFO.secret_json), {
        'licensing_privkey': privkey_args,
        'licensing_pubkey': pubkey_args
    })
    try:
        with open(path(PROJECTINFO.base_json), "r", encoding="utf-8") as f:
            user_base_settings = json.load(f)
    except FileNotFoundError:
        user_base_settings = {}
    public_settings = user_base_settings.get('public_settings', [])
    if 'licensing_pubkey' not in public_settings:
        public_settings.append('licensing_pubkey')
        update_json(path(PROJECTINFO.base_json), {'public_settings': public_settings})
        updated_base_json = True
    else:
        updated_base_json = False
    message = 'Saved a public/private key pair for licensing to:\n    %s.\n' \
              % PROJECTINFO.secret_json
    if updated_base_json:
        message += 'Also added "licensing_pubkey" to "public_settings" in' \
                   '\n    %s.\n' \
                   '(This lets your app read the public key when it runs.)\n' \
                   % PROJECTINFO.base_json
    message += '\nFor details on how to implement licensing for your ' \
               'application, see:\n '\
               '    https://build-system.fman.io/manual#licensing.'
    _LOG.info(message)


init_licensing.__doc__ = _("Generate public/private keys for licensing")


def _prompt_for_nbits():
    while True:
        nbits_str = prompt_for_value('Bit size', default='2048')
        try:
            return int(nbits_str)
        except ValueError:
            continue