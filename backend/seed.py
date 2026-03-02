"""Seed script: creates demo data (2 projects, 5 users, ~20 issues, comments)."""

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.project import Project, ProjectMember, MemberRole
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.comment import Comment
from app.dependencies import hash_password

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    # Clear existing data
    db.query(Comment).delete()
    db.query(Issue).delete()
    db.query(ProjectMember).delete()
    db.query(Project).delete()
    db.query(User).delete()
    db.commit()

    # Create users (password is "password123" for all demo users)
    pw = hash_password("password123")
    users = [
        User(name="Alice Johnson", email="alice@example.com", password_hash=pw),
        User(name="Bob Smith", email="bob@example.com", password_hash=pw),
        User(name="Carol Williams", email="carol@example.com", password_hash=pw),
        User(name="Dave Brown", email="dave@example.com", password_hash=pw),
        User(name="Eve Davis", email="eve@example.com", password_hash=pw),
    ]
    db.add_all(users)
    db.flush()

    # Create projects
    p1 = Project(name="IssueHub", key="IH", description="The bug tracker itself — dogfooding!")
    p2 = Project(name="Marketing Site", key="MKT", description="Company marketing website redesign")
    db.add_all([p1, p2])
    db.flush()

    # Memberships
    memberships = [
        ProjectMember(project_id=p1.id, user_id=users[0].id, role=MemberRole.maintainer),
        ProjectMember(project_id=p1.id, user_id=users[1].id, role=MemberRole.maintainer),
        ProjectMember(project_id=p1.id, user_id=users[2].id, role=MemberRole.member),
        ProjectMember(project_id=p1.id, user_id=users[3].id, role=MemberRole.member),
        ProjectMember(project_id=p2.id, user_id=users[1].id, role=MemberRole.maintainer),
        ProjectMember(project_id=p2.id, user_id=users[4].id, role=MemberRole.maintainer),
        ProjectMember(project_id=p2.id, user_id=users[0].id, role=MemberRole.member),
        ProjectMember(project_id=p2.id, user_id=users[3].id, role=MemberRole.member),
    ]
    db.add_all(memberships)
    db.flush()

    # Issues for IssueHub
    ih_issues = [
        Issue(project_id=p1.id, title="Login page returns 500 on empty email", description="Steps: go to /login, leave email blank, click submit. Server returns 500 instead of validation error.", status=IssueStatus.open, priority=IssuePriority.high, reporter_id=users[2].id, assignee_id=users[0].id),
        Issue(project_id=p1.id, title="Add password strength meter", description="Show a visual strength indicator when users type their password during signup.", status=IssueStatus.open, priority=IssuePriority.low, reporter_id=users[0].id),
        Issue(project_id=p1.id, title="Issue list pagination is off by one", description="Page 2 repeats the last item from page 1.", status=IssueStatus.in_progress, priority=IssuePriority.medium, reporter_id=users[3].id, assignee_id=users[1].id),
        Issue(project_id=p1.id, title="CORS error on production deploy", description="Frontend on Vercel can't reach the API. Need to whitelist the production URL.", status=IssueStatus.resolved, priority=IssuePriority.critical, reporter_id=users[1].id, assignee_id=users[0].id),
        Issue(project_id=p1.id, title="Add dark mode toggle", description="Users want a dark theme option.", status=IssueStatus.open, priority=IssuePriority.low, reporter_id=users[2].id),
        Issue(project_id=p1.id, title="Comment timestamps show UTC, not local time", description="All comment timestamps display in UTC. Should auto-convert to the user's local timezone.", status=IssueStatus.open, priority=IssuePriority.medium, reporter_id=users[3].id, assignee_id=users[2].id),
        Issue(project_id=p1.id, title="Email validation allows invalid TLDs", description="Signup accepts test@foo.invalidtld.", status=IssueStatus.in_progress, priority=IssuePriority.medium, reporter_id=users[0].id, assignee_id=users[1].id),
        Issue(project_id=p1.id, title="Rate-limit the login endpoint", description="Prevent brute-force attacks by rate-limiting /api/auth/login.", status=IssueStatus.open, priority=IssuePriority.high, reporter_id=users[1].id),
        Issue(project_id=p1.id, title="Migrate from SQLite to PostgreSQL for prod", description="SQLite is fine for dev but we need Postgres for production.", status=IssueStatus.closed, priority=IssuePriority.high, reporter_id=users[0].id, assignee_id=users[0].id),
        Issue(project_id=p1.id, title="Write API documentation with Swagger", description="FastAPI auto-generates docs but we need better descriptions.", status=IssueStatus.open, priority=IssuePriority.low, reporter_id=users[3].id),
        Issue(project_id=p1.id, title="Broken layout on mobile for issue detail", description="The comment thread overflows the viewport on screens < 400px.", status=IssueStatus.open, priority=IssuePriority.medium, reporter_id=users[2].id, assignee_id=users[0].id),
        Issue(project_id=p1.id, title="Add bulk status change for issues", description="Maintainers should be able to select multiple issues and change status at once.", status=IssueStatus.open, priority=IssuePriority.low, reporter_id=users[1].id),
    ]
    db.add_all(ih_issues)
    db.flush()

    # Issues for Marketing Site
    mkt_issues = [
        Issue(project_id=p2.id, title="Hero section image not loading", description="The main hero image returns 404 after the CDN migration.", status=IssueStatus.open, priority=IssuePriority.critical, reporter_id=users[4].id, assignee_id=users[1].id),
        Issue(project_id=p2.id, title="SEO meta tags missing on blog pages", description="Blog posts don't have og:title or og:description tags.", status=IssueStatus.in_progress, priority=IssuePriority.high, reporter_id=users[0].id, assignee_id=users[4].id),
        Issue(project_id=p2.id, title="Contact form doesn't validate phone number", description="Users can submit non-numeric phone numbers.", status=IssueStatus.open, priority=IssuePriority.medium, reporter_id=users[3].id),
        Issue(project_id=p2.id, title="Footer links point to old domain", description="Several footer links still reference the old .io domain.", status=IssueStatus.resolved, priority=IssuePriority.medium, reporter_id=users[1].id, assignee_id=users[4].id),
        Issue(project_id=p2.id, title="Lighthouse performance score below 70", description="Need to optimize images and reduce JS bundle size.", status=IssueStatus.open, priority=IssuePriority.high, reporter_id=users[4].id, assignee_id=users[0].id),
        Issue(project_id=p2.id, title="Add cookie consent banner", description="Required by GDPR. Show a banner and allow opt-out.", status=IssueStatus.open, priority=IssuePriority.high, reporter_id=users[0].id),
        Issue(project_id=p2.id, title="Blog RSS feed is broken", description="The /rss.xml endpoint returns malformed XML.", status=IssueStatus.open, priority=IssuePriority.low, reporter_id=users[3].id, assignee_id=users[1].id),
        Issue(project_id=p2.id, title="Pricing page needs A/B test setup", description="Marketing wants to test two pricing layouts. Need feature flag infrastructure.", status=IssueStatus.open, priority=IssuePriority.medium, reporter_id=users[1].id),
    ]
    db.add_all(mkt_issues)
    db.flush()

    # Comments
    all_issues = ih_issues + mkt_issues
    comments = [
        Comment(issue_id=ih_issues[0].id, author_id=users[0].id, body="I can reproduce this. The Pydantic validation is missing for the email field."),
        Comment(issue_id=ih_issues[0].id, author_id=users[2].id, body="Thanks Alice! Also happens when password is empty."),
        Comment(issue_id=ih_issues[2].id, author_id=users[1].id, body="Found the bug — the offset calculation uses 0-indexed pages but the frontend sends 1-indexed."),
        Comment(issue_id=ih_issues[2].id, author_id=users[3].id, body="That makes sense. The last item on each page was always duplicated."),
        Comment(issue_id=ih_issues[3].id, author_id=users[0].id, body="Fixed by adding the Vercel URL to CORS allow_origins. Deployed to prod."),
        Comment(issue_id=ih_issues[6].id, author_id=users[1].id, body="We should use a proper email validation library instead of regex."),
        Comment(issue_id=ih_issues[8].id, author_id=users[0].id, body="Migration done. Updated DATABASE_URL in production env vars."),
        Comment(issue_id=mkt_issues[0].id, author_id=users[1].id, body="The CDN bucket name changed. Updating the image URLs now."),
        Comment(issue_id=mkt_issues[1].id, author_id=users[4].id, body="Added og:title and og:description to the blog template. PR is up."),
        Comment(issue_id=mkt_issues[3].id, author_id=users[4].id, body="All footer links updated and verified. Closing this."),
    ]
    db.add_all(comments)
    db.commit()

    print(f"Seeded {len(users)} users, 2 projects, {len(all_issues)} issues, {len(comments)} comments.")
    print("Demo login: alice@example.com / password123")
    db.close()


if __name__ == "__main__":
    seed()
