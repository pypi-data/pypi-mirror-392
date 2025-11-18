certbot-dns-hcloud
==================

`Hetzner Cloud`_ DNS Authenticator plugin for Certbot

This plugin automates the process of completing a ``dns-01`` challenge by
creating, and subsequently removing, TXT records using the Hetzner Console API.

.. _Hetzner Cloud: https://console.hetzner.com/projects/
.. _certbot: https://certbot.eff.org/

Installation
------------

::

    pip install certbot-dns-hcloud


Named Arguments
---------------

To start using DNS authentication for HCloud, pass the following arguments on
certbot's command line:

==================================== ==============================================
``--authenticator dns-hcloud``       select the authenticator plugin (Required)

``--dns-hcloud-credentials``         Hetzner Console API credentials INI file.
                                     (Required)

``--dns-hcloud-propagation-seconds`` | waiting time for DNS to propagate before asking
                                     | the ACME server to verify the DNS record.
                                     | (Default: 60, Recommended: >= 120)
==================================== ==============================================


Credentials
-----------

An example ``credentials.ini`` file:

.. code-block:: ini

   dns_hcloud_api_token = j8foaU8u2irpupAHwaf...

The path to this file can be provided interactively or using the
``--dns-hcloud-credentials`` command-line argument. Certbot
records the path to this file for use during renewal, but does not store the
file's contents.

**Caution:** You should protect these API credentials as you would the
password to your ispconfig account. Users who can read this file can use these
credentials to issue arbitrary API calls on your behalf. Users who can cause
Certbot to run using these credentials can complete a ``dns-01`` challenge to
acquire new certificates or revoke existing certificates for associated
domains, even if those domains aren't being managed by this server.

Certbot will emit a warning if it detects that the credentials file can be
accessed by other users on your system. The warning reads "Unsafe permissions
on credentials configuration file", followed by the path to the credentials
file. This warning will be emitted each time Certbot uses the credentials file,
including for renewal, and cannot be silenced except by addressing the issue
(e.g., by using a command like ``chmod 600`` to restrict access to the file).


Examples
--------

To acquire a single certificate for both ``example.com`` and
``*.example.com``, waiting 900 seconds for DNS propagation:

.. code-block:: bash

   certbot certonly \
     --authenticator dns-hcloud \
     --dns-hcloud-credentials /etc/letsencrypt/.secrets/hetzner/certbot.ini \
     --dns-hcloud-propagation-seconds 900 \
     -d 'example.com' \
     -d '*.example.com'


It is suggested to secure the folder as follows:

.. code-block:: bash

   chown root:root /etc/letsencrypt/.secrets
   chmod 600 /etc/letsencrypt/.secrets


Recommended Setup (Debian 13)
-----------------------------

Install system dependencies

.. code-block:: bash

   sudo apt update
   sudo apt install -y python3 python3-venv python3-dev libaugeas-dev gcc git


I do generaly **not** recommended to run certbot as root. Therefor you create a new system user:

.. code-block:: bash
   
   sudo useradd -r -m certbot


Create letsencrypt directories and change permissions

.. code-block:: bash

   sudo mkdir -p {/etc,/var/log,/var/lib}/letsencrypt
   sudo chown -R certbot:certbot {/etc,/var/log,/var/lib}/letsencrypt
   sudo find {/etc,/var/log,/var/lib}/letsencrypt -type d -exec sudo chmod 755 {} +
   sudo find {/etc,/var/log,/var/lib}/letsencrypt -type f -exec sudo chmod 644 {} +


Install ``certbot`` and ``certbot-dns-hcloud`` inside a virtual environment

.. code-block:: bash
   
   # install venv for certbot
   sudo python3 -m venv /opt/certbot

   # change owner of the venv
   sudo chown certbot:certbot -R /opt/certbot

   # switch to certbot
   sudo -su certbot

   # install certbot
   /opt/certbot/bin/python -m pip install --upgrade pip
   /opt/certbot/bin/python -m pip install certbot certbot-dns-hcloud
   
   # create credentials file
   mkdir -p ~/.secrets/hetzner
   echo "dns_hcloud_api_token = <PLACE TOKEN HERE>" | tee ~/.secrets/hetzner/hcloud.ini
   chmod 600 ~/.secrets/hetzner/hcloud.ini

   # exit from certbot
   exit

   # expose certbot executable
   sudo ln -s /opt/certbot/bin/certbot /bin/certbot


If you did not replace the ``<PLACE TOKEN HERE>`` with your Hetzner Console API token, edit the
file with your prefered text editor i.e. ``nvim``, ``vi`` or ``nano``.

**Caution:** You have to use a `Hetzner Console <https://console.hetzner.com/>`_ API token. Dont't
confuse with the old `konsoleH <https://konsoleh.hetzner.com/>`_ API token. The DNS console has been
moved from ``konsoleH`` to ``Hetzner Console`` and now you have to use the ``Hetzner Cloud API`` to
manage your DNS zones.


Test if the installation was successful

.. code-block:: bash
   
   sudo -su certbot
   certbot certonly -n \
     --agree-tos \
     --dry-run \
     --test-cert \
     --authenticator dns-hcloud \
     --dns-hcloud-credentials ~/.secrets/hetzner/hcloud.ini \
     --dns-hcloud-propagation-seconds 120 \
     -d example.com \
     -d *.example.com
   exit

If certbot is installed correctly this should run without errors. If the challenge fails, change
``--dns-hcloud-credentials`` and check API token then try again. 

.. NOTE::
   You have to replace ``example.com`` with your domain.

Request your certificates

.. code-block:: bash
   
   sudo -su certbot
   certbot certonly -n \
     --agree-tos \
     --authenticator dns-hcloud \
     --dns-hcloud-credentials ~/.secrets/hetzner/hcloud.ini \
     --dns-hcloud-propagation-seconds 120 \
     -d example.com \
     -d *.example.com
   exit


Setup ``cron job`` for automated renewal

.. code-block:: bash

   # renewal twice a day
   echo "0 0,12 * * * certbot /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew -q" | sudo tee -a /etc/crontab > /dev/null

Setup ``cron job`` for automated updates

.. code-block:: bash

   # update every Monday at 6 am
   echo "0 6 * * 1 certbot /opt/certbot/bin/python -m pip install --upgrade certbot certbot-dns-hcloud" | sudo tee -a /etc/crontab > /dev/null
