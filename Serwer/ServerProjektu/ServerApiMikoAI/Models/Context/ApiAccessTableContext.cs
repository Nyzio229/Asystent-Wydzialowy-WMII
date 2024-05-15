using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;

namespace ServerApiMikoAI.Models.Context
{
    public class ApiAccessTableContext
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int id { get; set; }
        public string device_id { get; set; }
        public string api_key { get; set; }
        public bool is_active { get; set; }
    }
}
