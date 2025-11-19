# download the latest version of package from github, and run setup.py from that package
import os, sys, subprocess, zipfile
try:        from urllib.request import urlretrieve  # Python 3
except ImportError: from urllib import urlretrieve  # Python 2

# print messages directly to terminal, bypassing pip's pipe
def say(text):
    sys.stdout.write(text)
    sys.stdout.flush()
    if not sys.stdout.isatty():
        # output was redirected, but we still try to send the message to the terminal
        try:
            with open('/dev/tty','w') as out:
                out.write(text)
                out.flush()
        except:
            # /dev/tty may not exist or may not be writable!
            pass

say('Running '+__file__+'\nDownloading the latest version of package from github\n')
try:
    filename = 'agama.zip'
    dirname  = 'Agama-master'
    urlretrieve('https://github.com/GalacticDynamics-Oxford/Agama/archive/master.zip', filename)
    # unpack files from archive, they end up in the `dirname` folder
    zipf = zipfile.ZipFile(filename, 'r')  # unpack the archive
    zipf.extractall()
    zipf.close()
    # move files from `dirname` to the current directory, overwriting this setup.py by the one from the package
    os.remove(__file__)
    for fn in os.listdir(dirname):
        os.rename(os.path.join(dirname, fn), fn)
    # remove the downloaded archive and the now-empty folder `dirname`
    os.remove(filename)
    os.rmdir(dirname)
    # now transfer control to setup.py from the package
    cmdline = [sys.executable] + [x if x!='-c' else __file__ for x in sys.argv]
    say('Continuing installation by running the following command:\n' +
        ' '.join(['"%s"' % arg if ' ' in arg else arg for arg in cmdline]) + '\n')
    exit(subprocess.call(cmdline))
except Exception as ex:
    say('Exception: %s\n' % ex)
    exit(1)
