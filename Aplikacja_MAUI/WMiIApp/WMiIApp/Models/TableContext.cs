using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class TableContext
    {
        [JsonProperty("answerPL")]
        public string? AnswerPL { get; set; }
        [JsonProperty("questionPL")]
        public string? QuestionPL { get; set; }
        [JsonProperty("answerEN")]
        public string? AnswerEN { get; set; }
        [JsonProperty("questionEN")]
        public string? QuestionEN { get; set; }
    }
}
