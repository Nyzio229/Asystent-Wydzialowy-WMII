using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI.Models.Context {
    public class WMiIEmployeesDatabase : DbContext {
        public WMiIEmployeesDatabase(DbContextOptions<WMiIEmployeesDatabase> options) : base(options) {}

        public DbSet<WMiIEmployessTable> lampki { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder) {
            modelBuilder.Entity<WMiIEmployessTable>().HasKey(t => t.numerLampki);
        }
    }
}
