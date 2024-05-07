using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;

namespace ServerApiMikoAI.Models.Context {
    public class WMiIReservationTable {
        [Key]
        [Column(Order = 0)]
        public DateTime dzien { get; set; }
        [Key]
        [Column(Order = 1)]
        public int godz { get; set; }
        public string login { get; set; }
        public string powod { get; set; }
        [Key]
        [Column(Order = 2)]
        public string sala { get; set; }
        public DateTime ts { get; set; }
        public string rezerwujacy { get; set; }
        public bool konfliktIgnoruj { get; set; }
    }
}
