import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
import user_info
class TestNextEvent(unittest.TestCase):
   
    def setUp(self):
       # Sample test data with correct duration format (minutes:seconds)
       self.test_profile = {
           "key_events": {
               "event_1": {
                   "event_name": "Computer Vision Project",
                   "projected_begin_time": "18:00",
                   "projected_dur_mintues": "60:00",  # 60 minutes, 0 seconds
               },
               "event_2": {
                   "event_name": "Deep Learning Homework",
                   "projected_begin_time": "21:00",
                   "projected_dur_mintues": "120:30",  # 120 minutes, 30 seconds
               },
               "event_3": {
                   "event_name": "Quick Break",
                   "projected_begin_time": "19:30",
                   "projected_dur_mintues": "15:30",  # 15 minutes, 30 seconds
               },
               "event_4": {
                   "event_name": "",  # Empty event to test filtering
                   "projected_begin_time": "",
                   "projected_dur_mintues": "",
               }
           }
       }
    @patch('user_info.load_user_profile')
    def test_get_next_event(self, mock_load_profile):
        mock_load_profile.return_value = self.test_profile
       
       # Test cases with different current times
        test_cases = [
           # (current_time, expected_count, expected_statuses)
           ("17:00", 3, ["Upcoming", "Upcoming", "Upcoming"]),
           ("18:30", 3, ["Ongoing", "Upcoming", "Upcoming"]),
           ("19:45", 2, ["Ongoing", "Upcoming"]),
           ("21:30", 1, ["Ongoing"]),
           ("23:30", 0, [])
       ]
        for current_time_str, expected_count, expected_statuses in test_cases:
           with patch('datetime.datetime') as mock_datetime:
               # Mock current time
               mock_now = datetime.strptime(current_time_str, "%H:%M")
               mock_datetime.now.return_value = mock_now
               mock_datetime.strptime.side_effect = datetime.strptime
               next_events = user_info.get_next_event()
                # Test event count
               self.assertEqual(len(next_events), expected_count, 
                   f"Failed count for current time {current_time_str}")
               
               # Test event statuses
               if next_events:
                   actual_statuses = [details['status'] for details in next_events.values()]
                   self.assertEqual(actual_statuses, expected_statuses, 
                       f"Failed status check for current time {current_time_str}")
    def test_duration_parsing(self):
        test_durations = [
           ("60:00", 60, 0),    # 60 minutes
           ("120:30", 120, 30),  # 2 hours and 30 seconds
           ("15:45", 15, 45),    # 15 minutes and 45 seconds
           ("5:15", 5, 15)       # 5 minutes and 15 seconds
       ]
        for duration_str, expected_minutes, expected_seconds in test_durations:
           with patch('datetime.datetime') as mock_datetime:
                mock_datetime.strptime.side_effect = datetime.strptime
                mock_datetime.now.return_value = datetime.strptime("12:00", "%H:%M")
                    # Test by creating a simple event
                test_profile = {
                    "key_events": {
                       "test_event": {
                           "event_name": "Test Event",
                           "projected_begin_time": "12:00",
                           "projected_dur_mintues": duration_str
                       }
                   }
               }
                with patch('user_info.load_user_profile', return_value=test_profile):
                   next_events = user_info.get_next_event()
                   event = next_events.get("test_event")
                   
                   # Calculate expected end time
                   expected_end = datetime.strptime("12:00", "%H:%M") + \
                                timedelta(minutes=expected_minutes, seconds=expected_seconds)
                   actual_end = datetime.strptime("12:00", "%H:%M") + \
                               timedelta(minutes=float(duration_str.split(":")[0]), 
                                       seconds=float(duration_str.split(":")[1]))
                   
                   self.assertEqual(actual_end, expected_end, 
                       f"Failed duration parsing for {duration_str}")
    def test_invalid_duration_formats(self):
        invalid_durations = [
           "",           # Empty
           "invalid",    # Non-numeric
           "60",        # Missing seconds
           "60:xx",     # Invalid seconds
           "xx:00"      # Invalid minutes
       ]
        for invalid_duration in invalid_durations:
            test_profile = {
               "key_events": {
                   "test_event": {
                       "event_name": "Test Event",
                       "projected_begin_time": "12:00",
                       "projected_dur_mintues": invalid_duration
                   }
               }
           }
            with patch('user_info.load_user_profile', return_value=test_profile):
                next_events = user_info.get_next_event()
                self.assertEqual(len(next_events), 0, 
                   f"Should handle invalid duration format: {invalid_duration}")
if __name__ == '__main__':
   unittest.main()