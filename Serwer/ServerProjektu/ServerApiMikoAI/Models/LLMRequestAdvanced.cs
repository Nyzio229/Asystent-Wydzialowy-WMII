namespace ServerApiMikoAI.Models
{
    public class LLMRequestAdvanced
    {
        public string message { get; set; }

        public PreviousQuestion[] previousQuestions { get; set; }
    }
}
