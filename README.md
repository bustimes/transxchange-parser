(work in progress)

It uses
[xml.etree.ElementTree.iterparse](https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.iterparse),
which I found helped with parsing large files without using too much memory.

It doesn't implement the whole of the TransXChange standard, but attempts to handle all of the data available in Great Britain.
On bustimes.org, I use it with data from:

* Transport for London (`https://tfl.gov.uk/tfl/syndication/feeds/journey-planner-timetables.zip`)
* [the Traveline National Dataset](https://www.travelinedata.org.uk/)
* [the Bus Open Data Service](https://data.bus-data.dft.gov.uk/)
* [Stagecoach](https://www.stagecoachbus.com/open-data)
* [Passenger](https://data.discoverpassenger.com/)

It does some non-standard things in order to cope with the realities of the data that's out there:

### WaitTime

WaitTime – where a vehicle waits for a period of time at a stop. The PTI profile says this must be included in both the `To` and `From` elements for a stop:

```xml
<JourneyPatternTimingLink id="jptl_33">
    <From SequenceNumber="9">
        <StopPointRef>249000000327</StopPointRef>
        <TimingStatus>otherPoint</TimingStatus>
    </From>
    <To SequenceNumber="10">
        <!-- here --> 
        <WaitTime>PT2M</WaitTime>
        <StopPointRef>249000000328</StopPointRef>
        <TimingStatus>principalTimingPoint</TimingStatus>
    </To>
    <RouteLinkRef>rl_0002_9</RouteLinkRef>
    <RunTime>PT1M</RunTime>
</JourneyPatternTimingLink>
<JourneyPatternTimingLink id="jptl_34">
    <From SequenceNumber="10">
        <!-- and here -->
        <WaitTime>PT2M</WaitTime>
        <StopPointRef>249000000328</StopPointRef>
        <TimingStatus>principalTimingPoint</TimingStatus>
    </From>
    <To SequenceNumber="11">
        <StopPointRef>249000000301</StopPointRef>
        <TimingStatus>otherPoint</TimingStatus>
    </To>
    <RouteLinkRef>rl_0002_10</RouteLinkRef>
    <RunTime>PT1M</RunTime>
</JourneyPatternTimingLink>
```

As this is a bit controversial, and contradicts some other documentation that says the two wait times should be added (i.e. giving a total wait time of 4 minutes),
the parser will log a warning like this for each combination of `WaitTime`, `From/StopPointRef`  and `To/StopPointRef`:

```
correctly ignored second journey pattern wait time 00:02:00 at 249000000328
```

Due to a misunderstanding, some publishers do this instead – implying a wait at both consecutive stops:

```xml
<JourneyPatternTimingLink id="jptl_33">
    <From SequenceNumber="9">
        <StopPointRef>249000000327</StopPointRef>
        <TimingStatus>otherPoint</TimingStatus>
    </From>
    <To SequenceNumber="10">
        <StopPointRef>249000000328</StopPointRef>
        <TimingStatus>principalTimingPoint</TimingStatus>
    </To>
    <RouteLinkRef>rl_0002_9</RouteLinkRef>
    <RunTime>PT1M</RunTime>
</JourneyPatternTimingLink>
<JourneyPatternTimingLink id="jptl_34">
    <From SequenceNumber="10">
        <!-- here -->
        <WaitTime>PT2M</WaitTime>
        <StopPointRef>249000000328</StopPointRef>
        <TimingStatus>principalTimingPoint</TimingStatus>
    </From>
    <To SequenceNumber="11">
        <!-- and here -->
        <WaitTime>PT2M</WaitTime>
        <StopPointRef>249000000301</StopPointRef>
        <TimingStatus>otherPoint</TimingStatus>
    </To>
    <RouteLinkRef>rl_0002_10</RouteLinkRef>
    <RunTime>PT1M</RunTime>
</JourneyPatternTimingLink>

```

This parser will still interpret that "correctly", as a 2 minute wait at stop `249000000328` only, outputting a warning like this:

```
dodgily ignored second wait time 0:02:00 from 249000000328 to 249000000301
````

### DepartureDayShift

Publishers sometimes mistakenly set the `DepartureDayShift` for journeys starting slightly before midnight...

```xml
    <DepartureTime>23:50:00</DepartureTime>
    <DepartureDayShift>1</DepartureDayShift>
```

Suggesting a departure time of 47 hours and 58 minutes after midnight. 

(I think this problem has been fixed at the source now, so the relevant code could be safely removed.)

## You might not need this

Think carefully whether you need to parse TransXChange data at all.
GTFS (General Transit Feed Specification) is simpler, and it's used all around the world.
The Bus Open Data services offers timetable data in GTFS format, converted from TransXChange, for the whole of Great Britain or just the regions you're interested in:

* `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/all/`
  * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/england/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/east_anglia/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/east_midlands/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/east_anglia/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/london/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/north_east/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/north_west/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/south_east/`
    * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/south_west/`
  * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/scotland/`
  * `https://data.bus-data.dft.gov.uk/timetable/download/gtfs-file/wales/`

If must use TransXChange, there may be better parsers available. For example, [pytxc](https://github.com/ciaranmccormick/pytxc).
