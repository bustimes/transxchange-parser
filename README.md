(work in progress)

It uses
[xml.etree.ElementTree.iterparse](https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.iterparse),
which I found helped with parsing large files without using too much memory.

It has no dependencies, [noGDAL](https://kipcrossing.github.io/2021-01-03-noGDAL/), so in theory it can run in the browser using Pyodide.

It doesn't implement the whole of the TransXChange standard, but attempts to handle all of the data available in Great Britain.
On bustimes.org, I use it with data from:

* Transport for London (`https://tfl.gov.uk/tfl/syndication/feeds/journey-planner-timetables.zip`)
* [the Traveline National Dataset](https://www.travelinedata.org.uk/)
* [the Bus Open Data Service](https://data.bus-data.dft.gov.uk/)
* [Stagecoach](https://www.stagecoachbus.com/open-data)
* [Passenger](https://data.discoverpassenger.com/)
* Transport for Greater Manchester

## Usage

```python
import txc

document = txc.TransXChange("54.xml")

```

## You might not need this

Think carefully whether you need to parse TransXChange data at all.
GTFS (General Transit Feed Specification) is simpler, and is used all around the world.
The [Bus Open Data Service](https://data.bus-data.dft.gov.uk/timetable/download/#:~:text=data%20sets%20in-,GTFS,-format) offers timetable data in GTFS format, converted from TransXChange, for the whole of Great Britain or just the regions you're interested in:

* `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/all/`
  * 🏴󠁧󠁢󠁥󠁮󠁧󠁿 `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/england/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/east_anglia/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/east_midlands/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/east_anglia/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/london/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/north_east/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/north_west/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/south_east/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/south_west/`
  * 🏴󠁧󠁢󠁳󠁣󠁴󠁿 `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/scotland/`
  * 🏴󠁧󠁢󠁷󠁬󠁳󠁿 `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/wales/`

The National Data Library has an [archive](https://data.datalibrary.uk/transport/BODS-ARCHIVE/timetables/) of the above.

If you've thought about it and still want to use TransXChange, there may be better parsers available, such as [pytxc](https://github.com/ciaranmccormick/pytxc).
Or you could use the XML schema (`http://www.transxchange.org.uk/schema/2.4/TransXChange_general.xsd`), maybe with [xmlschema](https://pypi.org/project/xmlschema/).

## Future ideas

- Add type annotations
- Support creating and modifying TransXChange files, not just reading them
