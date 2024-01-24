namespace ServerApiMikoAI.Models
{
    public class Choice
    {
        public int Index { get; set; }
        public Message Message { get; set; }
        public string FinishReason { get; set; }
    }
}
