using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI.Models {
    public class VerificationDataBaseContext : DbContext {
        public VerificationDataBaseContext(DbContextOptions<VerificationDataBaseContext> options) : base(options) { }

        public DbSet<VerificationTableContext> verification_table { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder) {
            modelBuilder.Entity<VerificationTableContext>().HasKey(t => t.device_id);
        }
    }
}
