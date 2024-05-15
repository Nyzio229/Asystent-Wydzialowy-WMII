using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI.Models.Context
{
    public class VerificationDataBaseContext : DbContext
    {
        public VerificationDataBaseContext() {
        }

        public VerificationDataBaseContext(DbContextOptions<VerificationDataBaseContext> options) : base(options) { }

        public DbSet<VerificationTableContext> verification_table { get; set; }
        public DbSet<ApiAccessTableContext> api_access { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<VerificationTableContext>().HasKey(t => t.Id);
            modelBuilder.Entity<ApiAccessTableContext>().HasKey(t => t.device_id);
        }
    }
}
