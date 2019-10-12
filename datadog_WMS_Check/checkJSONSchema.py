import json
import sys
from schema import Schema, And, Use, Optional, SchemaError

#Insert here the template of the json schema to use for checking
template_schema = Schema({
    "RequestId": And(Use(str)),
    "Response": And(Use(int)),
    Optional("ResponseMessage"): And(Use(str)),
    "SuccessDetails": And(Use(str)),
     "Data": [
         {
             "ServiceCallID": And(Use(str)),
             "CallStartDate": And(Use(str)),
             "CallCompletionDate": And(Use(str)),
             "CallCompletionTime": And(Use(str)),
             "RemarksCallAndAppointment": And(Use(str)),
             "CallStatus": And(Use(str)),
             "NextAppointmentID": And(Use(int)),
             "NextAppointmentStartDate": And(Use(str)),
             "NextAppointmentTime": And(Use(str)),
             "LatestAppointmentCompletionDate": And(Use(str)),
             "NextAppointmentTechnicianName": And(Use(str)),
             "AppointmentStatus": And(Use(str)),
             "ResolutionOfCall": And(Use(str)),
             "Meters": [
                 {
                     "MeterID": And(Use(int)),
                     "MeterSize": And(Use(str)),
                     "DMA": And(Use(str)),
                     "MeterType": And(Use(str)),
                     "MeterReadingDate": And(Use(str)),
                     "MeterInitialReading": And(Use(str))
                 }
             ],
             "ProblemType": And(Use(str)),
             "LastUpdated": And(Use(str))
         }
     ]
})

idNotFound_schema = Schema({
    "RequestId": And(Use(str)),
    "Response": And(Use(str)),
    "ResponseMessage": And(Use(str)),
    "SuccessDetails": And(Use(str)),
    "Data": And(Use(str))
})

def compare_json_schema(resultFromAPI):
    try:
        template_schema.validate(resultFromAPI)
        return True
    except SchemaError:
            try:
                idNotFound_schema.validate(resultFromAPI)
                return True
            except SchemaError:
                return False

def main(resultFromAPI):
	# import testing JSON files to Python structures
    # resultFromAPI = load_json('WMSStructure.json')
    #resultFromAPI = sys.argv[0:]

	# compare first struct against second
    print('Compare JSON result is: {0}'.format(
		compare_json_schema(resultFromAPI)
	))

if (__name__ == '__main__'):
	main(sys.argv[0:])
