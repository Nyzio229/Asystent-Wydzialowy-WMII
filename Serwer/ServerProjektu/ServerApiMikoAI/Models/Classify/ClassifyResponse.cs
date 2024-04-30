namespace ServerApiMikoAI.Models.Classify
{
    public class ClassifyResponse
    {
        public string label { get; set; }

        public CategoryNavigationMetadata metadata { get; set; }
    }
}
