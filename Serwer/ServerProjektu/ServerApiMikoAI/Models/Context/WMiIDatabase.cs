using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI.Models.Context {
    public class WMiIDataBase : DbContext {
        public WMiIDataBase(DbContextOptions<WMiIDataBase> options) : base(options) {}

        public DbSet<WMiIEmployessTable> lampki { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder) {
            modelBuilder.Entity<WMiIEmployessTable>().HasKey(t => t.numerLampki);
        }
    }
}
