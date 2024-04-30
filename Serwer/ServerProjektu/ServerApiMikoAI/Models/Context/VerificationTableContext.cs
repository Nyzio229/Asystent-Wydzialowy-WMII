using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;

namespace ServerApiMikoAI.Models.Context
{
    public class VerificationTableContext
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }
        public string device_id { get; set; }
        public int verification_code { get; set; }

        public DateTime expiration_date { get; set; }

    }
}
