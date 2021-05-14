<p align="center">
  <a title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/Advanced-Systems/vector-assets/master/advanced-systems-logo-annotated.svg">
  </a>
</p>

<h1 align="center">Advanced Systems Security Policy</h1>

## Python Package Distribution

Installing third-party packages from PyPI always bears a certain risk: Source
distributions for instance are capable of running arbitrary code during the
installation procedure. By default, PIP attempts to install packages using wheels
if they are available (inter alia to circumvent the attack vector of arbitrary
code execution), but it will always fall back to source distributions if the
package doesn't provide any form of binary distribution. Different threat models
require different forms of protections, but this doesn't alter the fact that even
safe guards like the web of trust (WoT) only offer limited protection as in theory
anyone is qualified to become a package maintainer on PyPI, and even then end users
are vulnerable to typosquatting for all it takes is a moment of inadvertence to
accidentally install malware on their machine. As a rule of thumb, it is strongly
recommended to never run `pip` with root privileges. Use virtual environments to
isolate package installs for each individual project.

## DevSecOps Measures in Place

This project uses CodeQL that runs a static code analysis on each submission made
to this repository to detect malicious contributions before they creep into the
final release. CodeQL uses code queries created by a community of security
researchers on GitHub to help detect known security vulnerabilities in open-source
projects by following recommended security guidelines in all lines of works.

On top of that, dependatbot alerts are integrated in a pipeline of automated security
checks to help identify security vulnerabilities in dependencies.

By installing Python packages from PyPI you implicitly choose to trust not only
the repository owner, but anyone that is authorized to create new releases. In
the open-source software community it is therefore important to maintain a watchful
eye on compliance from any participating contributing party.

## Report A Vulnerability

Please email `dev.hentai-chan@outlook.com` to report any security-related issues
and include the following information in the text body:

- Your name and affiliation (if any)
- A description of the technical details of the vulnerabilities along with a step-by-step
  guide to help us reproduce your findings
- An explanation who can exploit this vulnerability, and what they gain when doing so
- Whether this vulnerability public or known to third parties
