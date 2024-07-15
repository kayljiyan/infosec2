namespace client.Schemas
{
    public class AppointmentData
    {
        public Appointment[]? data { get; set; }
        public class Appointment
        {
            public string? appointment_uuid { get; set; }
            public string? appointment_remarks { get; set; }
        }
    }
}