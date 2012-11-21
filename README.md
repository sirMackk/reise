## reise

### What is all this about?

While browsing the Internet, I stumbled upon a DNS tunneler. I never ran nor looked at the source code, but the idea stuck in my head as being pretty cool. Many months later when I was teaching myself Python I thought that coding this idea would be a great exercise. I wasn't wrong - so far it has involved awesome things like:

1. Sockets
2. Multithreading and queuing 
3. Working with lists and list comprehensions
4. Handling exceptions and errors
5. Knowledge of TCP and UDP

The main objective of this program is to pass HTTP traffic over UDP between two hosts in order to bypass things like captive portals or firewalls. With a bit of tweaking, it should be possible to create a chain of such proxies, even with alternating between TCP and UDP, because the two main classes were coded with this in mind, however I have yet to try test this out.

### Does this even work?

As of November 21st 2012, I have been able get this working using two hosts on my LAN which proves the main idea behind the whole project. I will test this in the field soon. There are a few quirks to work out such as:

1. Decreasing latency between two nodes.
2. Making sure that certain buffers are well managed.
3. Writing more unit tests for nose.
4. Creating a CLI interface.
5. Cleaning up the code to be more PEP8 compliant.

And more.

### License

Copyright (C) 2012  sirMackk

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.