namespace client.Schemas
{
    public class RequestData
    {
        public Request[]? data { get; set; }
        public class Request
        {
            public string? request_uuid { get; set; }
            public string? request_status { get; set; }
            public string? created_at { get; set; }
        }
    }
}