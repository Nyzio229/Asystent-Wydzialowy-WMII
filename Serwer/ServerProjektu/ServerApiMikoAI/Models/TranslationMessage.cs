namespace ServerApiMikoAI.Models
{
    public class TranslationMessage
    {
        public TranslationMessage() { }
        public TranslationMessage(string message, string translateFrom, string translateTo)
        {
            this.message = message;
            this.translateFrom = translateFrom;
            this.translateTo = translateTo;
        }

        public string message { get; set; }
        public string translateFrom { get; set; }
        public string translateTo { get; set; }
    }
}
