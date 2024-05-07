using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI.Models.Context {
    public class WMiIPlansDatabase: DbContext {
        public WMiIPlansDatabase(DbContextOptions<WMiIPlansDatabase> options) : base(options) { }

        public DbSet<WMiIReservationTable> Rezerwacje { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder) {
            modelBuilder.Entity<WMiIReservationTable>().HasKey(t => new { t.dzien, t.godz, t.sala });
        }
    }
}
