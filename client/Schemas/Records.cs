namespace client.Schemas
{
    public class RecordData
    {
        public Record[]? data { get; set; }
        public class Record
        {
            public string? record_uuid { get; set; }
            public string? record_content { get; set; }
            public string? doctor_name { get; set; }
            public string? patient_name { get; set; }
        }
    }
}