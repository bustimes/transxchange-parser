(work in progress)

It uses
[xml.etree.ElementTree.iterparse](https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.iterparse),
which I found helped with parsing large files without using too much memory.

It doesn't implement the whole of the TranxXChange standard, but attempts to handle all of the data available in Great Britain.
On bustimes.org, I use it with data from
Transport for London (`https://tfl.gov.uk/tfl/syndication/feeds/journey-planner-timetables.zip`),
the Traveline National Dataset,
and the Bus Open Data Service.

It does some non-standard things in order to cope with the realities of the data that's out there:

## WaitTime

WaitTime – where a vehicle waits for a period of time at a stop. The PTI profile says this must be included in both the `To` and `From` elements for a stop:

```xml
<JourneyPatternTimingLink id="jptl_33">
    <From SequenceNumber="9">
        <StopPointRef>249000000327</StopPointRef>
        <TimingStatus>otherPoint</TimingStatus>
    </From>
    <To SequenceNumber="10">
        <WaitTime>PT2M</WaitTime>
        <StopPointRef>249000000328</StopPointRef>
        <TimingStatus>principalTimingPoint</TimingStatus>
    </To>
    <RouteLinkRef>rl_0002_9</RouteLinkRef>
    <RunTime>PT1M</RunTime>
</JourneyPatternTimingLink>
<JourneyPatternTimingLink id="jptl_34">
    <From SequenceNumber="10">
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
the parser will log a warning like this for each permutation of `WaitTime`, `From/StopPointRefz and `To/StopPointRef`:

```
correctly ignored second journey pattern wait time 00:02:00 at 249000000328
```

Due to a misunderstanding, some publishers do this instead – suggesting a wait at both consecutive stops:

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
        <WaitTime>PT2M</WaitTime>
        <StopPointRef>249000000328</StopPointRef>
        <TimingStatus>principalTimingPoint</TimingStatus>
    </From>
    <To SequenceNumber="11">
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

## DepartureDayShift

Publushers sometimes mistakenly set the `DepartureDayShift` for journeys starting slightly before midnight...
