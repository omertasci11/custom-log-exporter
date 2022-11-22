# Custom Log Exporter Windows Event Viewer

We get the failed rdp logs (EventID=4625) in the security section and then we get geolocation information by sending the IP information obtained from these logs to the 3rd party API (https://ipgeolocation.io/). We write all this information in a log file that we have created in the appropriate log format.

## Installation

:warning: Run as Administrator :warning:

`git clone https://github.com/omertasci11/custom-log-exporter.git`

`pip install pywin32`

`pip install python-dateutil`

`pip install requests`
