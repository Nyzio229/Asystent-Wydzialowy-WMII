using Microsoft.OpenApi.Any;
using System.Collections;
using System.ComponentModel.DataAnnotations;

namespace ServerApiMikoAI.Models
{
    /// <summary>
    /// 
    /// </summary>
    public class LLMRequest
    {
        public Message messages { get; set; }
    }
}
