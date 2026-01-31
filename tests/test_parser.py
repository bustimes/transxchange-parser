"""Tests for the TransXChange parser using real test data"""

import os
from unittest import TestCase

from txc import txc


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data")
COLCHESTER_FILE = os.path.join(
    TEST_DATA_DIR,
    "54-FEAO054--FESX-Colchester-2025-09-07-CR20_Exports-CF_C59_Update-BODS_V1_1.xml",
)


class TransXChangeParserTest(TestCase):
    """Tests for the main TransXChange parser"""

    @classmethod
    def setUpClass(cls):
        """Parse the test file once for all tests"""
        with open(COLCHESTER_FILE) as f:
            cls.txc = txc.TransXChange(f)

    def test_stops_parsed(self):
        """Test that stops were parsed"""
        self.assertGreater(len(self.txc.stops), 0)
        # Check a specific stop
        stop = self.txc.stops.get("150033038003")
        self.assertIsNotNone(stop)
        self.assertEqual(stop.common_name, "Osborne Street")

    def test_services_parsed(self):
        """Test that services were parsed"""
        self.assertGreater(len(self.txc.services), 0)

    def test_routes_parsed(self):
        """Test that routes were parsed"""
        self.assertGreater(len(self.txc.routes), 0)

    def test_route_sections_parsed(self):
        """Test that route sections were parsed"""
        self.assertGreater(len(self.txc.route_sections), 0)

    def test_journeys_parsed(self):
        """Test that vehicle journeys were parsed"""
        self.assertGreater(len(self.txc.journeys), 0)

    def test_service_properties(self):
        """Test that service properties are accessible"""
        for service in self.txc.services.values():
            # Access various properties
            self.assertIsNotNone(service.service_code)
            self.assertIsNotNone(service.operating_period)
            self.assertIsInstance(service.lines, list)
            self.assertIsInstance(service.journey_patterns, dict)

    def test_journey_pattern_properties(self):
        """Test journey pattern properties"""
        for service in self.txc.services.values():
            for pattern in service.journey_patterns.values():
                self.assertIsNotNone(pattern.id)
                self.assertIsInstance(pattern.sections, list)

    def test_vehicle_journey_properties(self):
        """Test vehicle journey properties"""
        journey = self.txc.journeys[0]
        self.assertIsNotNone(journey.code)
        self.assertIsNotNone(journey.departure_time)
        self.assertIsNotNone(journey.service_ref)
        self.assertIsNotNone(journey.line_ref)

    def test_get_journeys(self):
        """Test the get_journeys method"""
        # Get a service code and line ID from an existing journey
        journey = self.txc.journeys[0]
        service_code = journey.service_ref
        line_id = journey.line_ref

        journeys = self.txc.get_journeys(service_code, line_id)
        self.assertIsInstance(journeys, list)
        self.assertGreater(len(journeys), 0)
        for j in journeys:
            self.assertEqual(j.service_ref, service_code)
            self.assertEqual(j.line_ref, line_id)

    def test_journey_get_timinglinks(self):
        """Test the get_timinglinks method on a journey"""
        journey = self.txc.journeys[0]
        timing_links = list(journey.get_timinglinks())
        self.assertGreater(len(timing_links), 0)

    def test_journey_get_times(self):
        """Test the get_times method on a journey"""
        journey = self.txc.journeys[0]
        times = list(journey.get_times())
        self.assertGreater(len(times), 0)
        # Each time should be a Cell
        for cell in times:
            self.assertIsInstance(cell, txc.Cell)
            self.assertIsNotNone(cell.stopusage)
            self.assertIsNotNone(cell.arrival_time)
            self.assertIsNotNone(cell.departure_time)

    def test_stop_str(self):
        """Test Stop __str__ method"""
        stop = self.txc.stops.get("150033038003")
        self.assertIsNotNone(stop)
        stop_str = str(stop)
        self.assertIn("Osborne Street", stop_str)

    def test_vehicle_journey_str(self):
        """Test VehicleJourney __str__ method"""
        journey = self.txc.journeys[0]
        journey_str = str(journey)
        self.assertIsNotNone(journey_str)

    def test_line_properties(self):
        """Test Line properties"""
        for service in self.txc.services.values():
            for line in service.lines:
                self.assertIsNotNone(line.id)
                self.assertIsNotNone(line.line_name)

    def test_route_link_properties(self):
        """Test RouteLink properties"""
        for route_section in self.txc.route_sections.values():
            for link in route_section.links:
                self.assertIsNotNone(link.id)
                self.assertIsNotNone(link.from_stop)
                self.assertIsNotNone(link.to_stop)

    def test_journey_pattern_get_timinglinks(self):
        """Test JourneyPattern get_timinglinks"""
        for service in self.txc.services.values():
            for pattern in service.journey_patterns.values():
                links = list(pattern.get_timinglinks())
                self.assertIsInstance(links, list)
                break  # Just test one
            break  # Just test one service


class ParseTimeTest(TestCase):
    """Tests for the parse_time function"""

    def test_parse_time(self):
        """Test parsing time strings"""
        import datetime

        result = txc.parse_time("08:30:00")
        self.assertEqual(result, datetime.timedelta(hours=8, minutes=30))

        result = txc.parse_time("23:59:59")
        self.assertEqual(
            result, datetime.timedelta(hours=23, minutes=59, seconds=59)
        )

        result = txc.parse_time("00:00:00")
        self.assertEqual(result, datetime.timedelta())


class StopTest(TestCase):
    """Tests for the Stop class"""

    def test_stop_with_only_atco_code(self):
        """Test Stop with only ATCO code"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <StopPoint>
                <AtcoCode>123456789</AtcoCode>
            </StopPoint>
            """
        )
        stop = txc.Stop(element)
        self.assertEqual(stop.atco_code, "123456789")
        self.assertEqual(str(stop), "123456789")

    def test_stop_with_indicator(self):
        """Test Stop with indicator"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <StopPoint>
                <AtcoCode>123456789</AtcoCode>
                <CommonName>Test Stop</CommonName>
                <Indicator>Stop A</Indicator>
            </StopPoint>
            """
        )
        stop = txc.Stop(element)
        self.assertEqual(str(stop), "Test Stop (Stop A)")

    def test_stop_with_locality(self):
        """Test Stop with locality"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <StopPoint>
                <AtcoCode>123456789</AtcoCode>
                <CommonName>Market Square</CommonName>
                <LocalityName>Colchester</LocalityName>
            </StopPoint>
            """
        )
        stop = txc.Stop(element)
        self.assertEqual(str(stop), "Colchester Market Square")

    def test_stop_with_locality_in_name(self):
        """Test Stop where locality is already in name"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <StopPoint>
                <AtcoCode>123456789</AtcoCode>
                <CommonName>Colchester Market Square</CommonName>
                <LocalityName>Colchester</LocalityName>
            </StopPoint>
            """
        )
        stop = txc.Stop(element)
        # Locality not repeated if already in name
        self.assertEqual(str(stop), "Colchester Market Square")

    def test_stop_with_descriptor_common_name(self):
        """Test Stop with CommonName under Descriptor"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <StopPoint>
                <AtcoCode>123456789</AtcoCode>
                <Descriptor>
                    <CommonName>Descriptor Name</CommonName>
                </Descriptor>
            </StopPoint>
            """
        )
        stop = txc.Stop(element)
        self.assertEqual(stop.common_name, "Descriptor Name")


class DayOfWeekTest(TestCase):
    """Tests for the DayOfWeek class"""

    def test_day_from_string(self):
        """Test creating DayOfWeek from string"""
        day = txc.DayOfWeek("Monday")
        self.assertEqual(day.day, 0)
        self.assertEqual(repr(day), "Monday")

    def test_day_from_int(self):
        """Test creating DayOfWeek from int"""
        day = txc.DayOfWeek(4)
        self.assertEqual(day.day, 4)
        self.assertEqual(repr(day), "Friday")

    def test_day_equality_with_int(self):
        """Test DayOfWeek equality with int"""
        day = txc.DayOfWeek("Wednesday")
        self.assertEqual(day, 2)
        self.assertNotEqual(day, 3)

    def test_day_equality_with_day(self):
        """Test DayOfWeek equality with another DayOfWeek"""
        day1 = txc.DayOfWeek("Friday")
        day2 = txc.DayOfWeek(4)
        self.assertEqual(day1, day2)


class ServicedOrganisationTest(TestCase):
    """Tests for ServicedOrganisation"""

    def test_serviced_organisation(self):
        """Test parsing a ServicedOrganisation"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <ServicedOrganisation>
                <OrganisationCode>SD</OrganisationCode>
                <Name>School Days</Name>
                <WorkingDays>
                    <DateRange>
                        <StartDate>2025-09-01</StartDate>
                        <EndDate>2025-10-24</EndDate>
                    </DateRange>
                </WorkingDays>
                <Holidays>
                    <DateRange>
                        <StartDate>2025-10-25</StartDate>
                        <EndDate>2025-11-02</EndDate>
                    </DateRange>
                </Holidays>
            </ServicedOrganisation>
            """
        )
        org = txc.ServicedOrganisation(element)
        self.assertEqual(org.code, "SD")
        self.assertEqual(org.name, "School Days")
        self.assertEqual(len(org.working_days), 1)
        self.assertEqual(len(org.holidays), 1)
        self.assertEqual(str(org), "School Days")

    def test_serviced_organisation_no_name(self):
        """Test ServicedOrganisation without name falls back to code"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <ServicedOrganisation>
                <OrganisationCode>ABC</OrganisationCode>
            </ServicedOrganisation>
            """
        )
        org = txc.ServicedOrganisation(element)
        self.assertEqual(str(org), "ABC")


class ServicedOrganisationDayTypeTest(TestCase):
    """Tests for ServicedOrganisationDayType"""

    def test_working_days_operation(self):
        """Test DaysOfOperation + WorkingDays"""
        import xml.etree.ElementTree as ET

        org_element = ET.fromstring(
            """
            <ServicedOrganisation>
                <OrganisationCode>SD</OrganisationCode>
                <Name>School</Name>
            </ServicedOrganisation>
            """
        )
        orgs = {"SD": txc.ServicedOrganisation(org_element)}

        day_type = txc.ServicedOrganisationDayType(
            orgs, "SD", operation=True, working=True
        )
        self.assertEqual(repr(day_type), "School days")

    def test_holidays_operation(self):
        """Test DaysOfOperation + Holidays"""
        import xml.etree.ElementTree as ET

        org_element = ET.fromstring(
            """
            <ServicedOrganisation>
                <OrganisationCode>SD</OrganisationCode>
                <Name>School</Name>
            </ServicedOrganisation>
            """
        )
        orgs = {"SD": txc.ServicedOrganisation(org_element)}

        day_type = txc.ServicedOrganisationDayType(
            orgs, "SD", operation=True, working=False
        )
        self.assertEqual(repr(day_type), "School holidays")

    def test_working_days_non_operation(self):
        """Test DaysOfNonOperation + WorkingDays"""
        import xml.etree.ElementTree as ET

        org_element = ET.fromstring(
            """
            <ServicedOrganisation>
                <OrganisationCode>SD</OrganisationCode>
                <Name>School</Name>
            </ServicedOrganisation>
            """
        )
        orgs = {"SD": txc.ServicedOrganisation(org_element)}

        day_type = txc.ServicedOrganisationDayType(
            orgs, "SD", operation=False, working=True
        )
        self.assertEqual(repr(day_type), "School holidays")

    def test_holidays_non_operation(self):
        """Test DaysOfNonOperation + Holidays"""
        import xml.etree.ElementTree as ET

        org_element = ET.fromstring(
            """
            <ServicedOrganisation>
                <OrganisationCode>SD</OrganisationCode>
                <Name>School</Name>
            </ServicedOrganisation>
            """
        )
        orgs = {"SD": txc.ServicedOrganisation(org_element)}

        day_type = txc.ServicedOrganisationDayType(
            orgs, "SD", operation=False, working=False
        )
        self.assertEqual(repr(day_type), "School days")


class OperatingProfileExtendedTest(TestCase):
    """Extended tests for OperatingProfile"""

    def test_day_range(self):
        """Test MondayToFriday style day range"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <OperatingProfile>
                <RegularDayType>
                    <DaysOfWeek>
                        <MondayToFriday />
                    </DaysOfWeek>
                </RegularDayType>
            </OperatingProfile>
            """
        )
        profile = txc.OperatingProfile(element, None)
        self.assertEqual(len(profile.regular_days), 5)
        days = [d.day for d in profile.regular_days]
        self.assertEqual(days, [0, 1, 2, 3, 4])

    def test_special_days_nonoperation(self):
        """Test special days of non-operation"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <OperatingProfile>
                <RegularDayType>
                    <DaysOfWeek>
                        <Monday />
                    </DaysOfWeek>
                </RegularDayType>
                <SpecialDaysOperation>
                    <DaysOfNonOperation>
                        <DateRange>
                            <StartDate>2025-12-25</StartDate>
                            <EndDate>2025-12-25</EndDate>
                        </DateRange>
                    </DaysOfNonOperation>
                </SpecialDaysOperation>
            </OperatingProfile>
            """
        )
        profile = txc.OperatingProfile(element, None)
        self.assertEqual(len(profile.nonoperation_days), 1)

    def test_special_days_operation(self):
        """Test special days of operation"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <OperatingProfile>
                <RegularDayType>
                    <DaysOfWeek>
                        <Monday />
                    </DaysOfWeek>
                </RegularDayType>
                <SpecialDaysOperation>
                    <DaysOfOperation>
                        <DateRange>
                            <StartDate>2025-12-26</StartDate>
                            <EndDate>2025-12-26</EndDate>
                        </DateRange>
                    </DaysOfOperation>
                </SpecialDaysOperation>
            </OperatingProfile>
            """
        )
        profile = txc.OperatingProfile(element, None)
        self.assertEqual(len(profile.operation_days), 1)


class ParseDurationTest(TestCase):
    """Tests for the parse_duration function"""

    def test_parse_minutes(self):
        """Test parsing duration with minutes only"""
        import datetime

        result = txc.parse_duration("PT10M")
        self.assertEqual(result, datetime.timedelta(minutes=10))

    def test_parse_hours_minutes(self):
        """Test parsing duration with hours and minutes"""
        import datetime

        result = txc.parse_duration("PT1H30M")
        self.assertEqual(result, datetime.timedelta(hours=1, minutes=30))

    def test_parse_seconds(self):
        """Test parsing duration with seconds"""
        import datetime

        result = txc.parse_duration("PT45S")
        self.assertEqual(result, datetime.timedelta(seconds=45))

    def test_parse_full(self):
        """Test parsing duration with hours, minutes and seconds"""
        import datetime

        result = txc.parse_duration("PT2H15M30S")
        self.assertEqual(
            result, datetime.timedelta(hours=2, minutes=15, seconds=30)
        )

    def test_invalid_duration(self):
        """Test that invalid duration raises error"""
        with self.assertRaises(ValueError):
            txc.parse_duration("10M")


class StopWithStopPointRefTest(TestCase):
    """Test Stop parsing with StopPointRef instead of AtcoCode"""

    def test_stop_with_stoppoint_ref(self):
        """Test Stop with StopPointRef"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <AnnotatedStopPointRef>
                <StopPointRef>150033038003</StopPointRef>
                <CommonName>Test Stop</CommonName>
            </AnnotatedStopPointRef>
            """
        )
        stop = txc.Stop(element)
        self.assertEqual(stop.atco_code, "150033038003")
        self.assertEqual(stop.common_name, "Test Stop")


class CellTest(TestCase):
    """Tests for the Cell class"""

    def test_cell_with_different_times(self):
        """Test Cell with different arrival and departure times"""
        import datetime

        # Create a minimal stopusage mock
        class MockStopUsage:
            pass

        stopusage = MockStopUsage()
        arrival = datetime.timedelta(hours=8)
        departure = datetime.timedelta(hours=8, minutes=5)

        cell = txc.Cell(stopusage, arrival, departure, None, None)
        self.assertTrue(cell.wait_time)
        self.assertEqual(cell.arrival_time, arrival)
        self.assertEqual(cell.departure_time, departure)

    def test_cell_with_same_times(self):
        """Test Cell with same arrival and departure times"""
        import datetime

        class MockStopUsage:
            pass

        stopusage = MockStopUsage()
        time = datetime.timedelta(hours=8)

        cell = txc.Cell(stopusage, time, time, None, None)
        self.assertIsNone(cell.wait_time)


class WarnOnceTest(TestCase):
    """Test the warn_once function"""

    def test_warn_once(self):
        """Test that warn_once can be called"""
        # Just verify it doesn't raise
        txc.warn_once("test warning %s", "arg")


class DeadRunTest(TestCase):
    """Tests for get_deadruns and get_deadrun_ref"""

    def test_get_deadrun_ref_none(self):
        """Test get_deadrun_ref with None element"""
        result = txc.get_deadrun_ref(None)
        self.assertIsNone(result)

    def test_get_deadrun_ref_with_element(self):
        """Test get_deadrun_ref with element"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <StartDeadRun>
                <ShortWorking>
                    <JourneyPatternTimingLinkRef>JPL_123</JourneyPatternTimingLinkRef>
                </ShortWorking>
            </StartDeadRun>
            """
        )
        result = txc.get_deadrun_ref(element)
        self.assertEqual(result, "JPL_123")

    def test_get_deadruns(self):
        """Test get_deadruns"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <VehicleJourney>
                <StartDeadRun>
                    <ShortWorking>
                        <JourneyPatternTimingLinkRef>JPL_START</JourneyPatternTimingLinkRef>
                    </ShortWorking>
                </StartDeadRun>
                <EndDeadRun>
                    <ShortWorking>
                        <JourneyPatternTimingLinkRef>JPL_END</JourneyPatternTimingLinkRef>
                    </ShortWorking>
                </EndDeadRun>
            </VehicleJourney>
            """
        )
        start, end = txc.get_deadruns(element)
        self.assertEqual(start, "JPL_START")
        self.assertEqual(end, "JPL_END")


class VehicleTypeTest(TestCase):
    """Tests for VehicleType"""

    def test_vehicle_type(self):
        """Test VehicleType parsing"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <VehicleType>
                <VehicleTypeCode>SB</VehicleTypeCode>
                <Description>Single Deck Bus</Description>
            </VehicleType>
            """
        )
        vtype = txc.VehicleType(element)
        self.assertEqual(vtype.code, "SB")
        self.assertEqual(vtype.description, "Single Deck Bus")


class BlockTest(TestCase):
    """Tests for Block"""

    def test_block(self):
        """Test Block parsing"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <Block>
                <BlockNumber>BLK001</BlockNumber>
                <Description>Morning Block</Description>
            </Block>
            """
        )
        block = txc.Block(element)
        self.assertEqual(block.code, "BLK001")
        self.assertEqual(block.description, "Morning Block")


class RouteTest(TestCase):
    """Tests for Route"""

    def test_route(self):
        """Test Route parsing"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <Route id="RT001">
                <RouteSectionRef>RS001</RouteSectionRef>
                <RouteSectionRef>RS002</RouteSectionRef>
            </Route>
            """
        )
        route = txc.Route(element)
        self.assertEqual(route.id, "RT001")
        self.assertEqual(route.route_section_refs, ["RS001", "RS002"])


class LineTest(TestCase):
    """Tests for Line"""

    def test_line_with_brand(self):
        """Test Line with brand in name"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <Line id="L001">
                <LineName>54 | Colchester Buses</LineName>
                <LineColour>FF0000</LineColour>
            </Line>
            """
        )
        line = txc.Line(element)
        self.assertEqual(line.id, "L001")
        self.assertEqual(line.line_name, "54")
        self.assertEqual(line.line_brand, "Colchester Buses")
        self.assertEqual(line.colour, "FF0000")

    def test_line_without_brand(self):
        """Test Line without brand"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <Line id="L002">
                <LineName>55</LineName>
            </Line>
            """
        )
        line = txc.Line(element)
        self.assertEqual(line.line_name, "55")
        self.assertEqual(line.line_brand, "")

    def test_line_with_descriptions(self):
        """Test Line with outbound/inbound descriptions"""
        import xml.etree.ElementTree as ET

        element = ET.fromstring(
            """
            <Line id="L003">
                <LineName>56</LineName>
                <OutboundDescription>
                    <Description>To Town Centre</Description>
                </OutboundDescription>
                <InboundDescription>
                    <Description>To Station</Description>
                </InboundDescription>
            </Line>
            """
        )
        line = txc.Line(element)
        self.assertEqual(line.outbound_description, "To Town Centre")
        self.assertEqual(line.inbound_description, "To Station")


class CellWithNoneTest(TestCase):
    """Test Cell with None times"""

    def test_cell_with_none_arrival(self):
        """Test Cell with None arrival time"""

        class MockStopUsage:
            pass

        stopusage = MockStopUsage()
        cell = txc.Cell(stopusage, None, None, None, None)
        self.assertIsNone(cell.wait_time)
