using System.Text.Json.Serialization;

namespace WMiIApp.Models
{
    public class Message
    {
        public string Content { get; set; }
        public string Role { get; set; }
        //content, role
    }

    [JsonSerializable(typeof(Message))]
    internal sealed partial class MessageContext : JsonSerializerContext
    {

    }
}
