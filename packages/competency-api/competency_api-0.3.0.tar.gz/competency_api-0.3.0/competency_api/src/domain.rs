//! Domain taxonomy for skill categorization
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SkillDomain {
    // Business domains
    Finance,
    Marketing,
    Sales,
    HR,
    Operations,

    // Technical domains
    SoftwareDevelopment,
    DataScience,
    ITSupport,
    DevOps,
    Cybersecurity,

    // Professional skills
    Leadership,
    Communication,
    ProjectManagement,

    // Generic/Unknown
    General,
}

impl SkillDomain {
    /// Calculate cross-domain penalty (0.0 = no penalty, 1.0 = full penalty)
    pub fn cross_domain_penalty(&self, other: &SkillDomain) -> f64 {
        if self == other {
            return 0.0; // Same domain, no penalty
        }

        match (self, other) {
            // Related domains - small penalty
            (SkillDomain::SoftwareDevelopment, SkillDomain::DataScience)
            | (SkillDomain::DataScience, SkillDomain::SoftwareDevelopment) => 0.15,

            (SkillDomain::SoftwareDevelopment, SkillDomain::DevOps)
            | (SkillDomain::DevOps, SkillDomain::SoftwareDevelopment) => 0.10,

            (SkillDomain::Marketing, SkillDomain::Sales)
            | (SkillDomain::Sales, SkillDomain::Marketing) => 0.20,

            // Professional skills transfer across domains - medium penalty
            (SkillDomain::Leadership, _)
            | (_, SkillDomain::Leadership)
            | (SkillDomain::Communication, _)
            | (_, SkillDomain::Communication)
            | (SkillDomain::ProjectManagement, _)
            | (_, SkillDomain::ProjectManagement) => 0.30,

            // General skills
            (SkillDomain::General, _) | (_, SkillDomain::General) => 0.20,

            // Unrelated domains - heavy penalty
            _ => 0.60,
        }
    }

    /// Classify a skill into a domain using keyword matching
    pub fn classify_skill(skill_name: &str) -> SkillDomain {
        let lower = skill_name.to_lowercase();

        // Finance keywords - comprehensive financial domain coverage
        if lower.contains("financ")
            || lower.contains("account")
            || lower.contains("budget")
            || lower.contains("forecast")
            || lower.contains("audit")
            || lower.contains("tax")
            || lower.contains("investment")
            || lower.contains("treasury")
            || lower.contains("payroll")
            || lower.contains("bookkeep")
            || lower.contains("ledger")
            || lower.contains("gaap")
            || lower.contains("ifrs")
            || lower.contains("sox")
            || lower.contains("revenue")
            || lower.contains("expense")
            || lower.contains("cash flow")
            || lower.contains("financial report")
            || lower.contains("financial analys")
            || lower.contains("financial model")
            || lower.contains("valuation")
            || lower.contains("mergers")
            || lower.contains("acquisitions")
            || lower.contains("m&a")
            || lower.contains("fp&a")
            || lower.contains("controller")
            || lower.contains("cfo")
        {
            return SkillDomain::Finance;
        }

        // Marketing keywords - comprehensive marketing domain coverage
        if lower.contains("market")
            || lower.contains("brand")
            || lower.contains("campaign")
            || lower.contains("advertis")
            || lower.contains("seo")
            || lower.contains("content")
            || lower.contains("social media")
            || lower.contains("digital market")
            || lower.contains("email market")
            || lower.contains("growth hack")
            || lower.contains("demand gen")
            || lower.contains("lead gen")
            || lower.contains("copywriting")
            || lower.contains("sem")
            || lower.contains("ppc")
            || lower.contains("google ads")
            || lower.contains("facebook ads")
            || lower.contains("influencer")
            || lower.contains("public relations")
            || lower.contains("pr ")
            || lower.contains("brand awareness")
            || lower.contains("brand strategy")
            || lower.contains("customer acquisition")
            || lower.contains("cac")
            || lower.contains("conversion")
            || lower.contains("funnel")
            || lower.contains("engagement")
            || lower.contains("analytics")
            || lower.contains("google analytics")
            || lower.contains("a/b test")
            || lower.contains("cro")
            || lower.contains("inbound")
            || lower.contains("outbound market")
        {
            return SkillDomain::Marketing;
        }

        // Sales keywords - comprehensive sales domain coverage
        if lower.contains("sales")
            || lower.contains("sell")
            || lower.contains("closing")
            || lower.contains("prospecting")
            || lower.contains("cold call")
            || lower.contains("warm call")
            || lower.contains("pipeline")
            || lower.contains("quota")
            || lower.contains("territory")
            || lower.contains("account executive")
            || lower.contains("business development")
            || lower.contains("bdr")
            || lower.contains("sdr")
            || lower.contains("inside sales")
            || lower.contains("outside sales")
            || lower.contains("enterprise sales")
            || lower.contains("b2b sales")
            || lower.contains("b2c sales")
            || lower.contains("saas sales")
            || lower.contains("solution sell")
            || lower.contains("consultative sell")
            || lower.contains("negotiation")
            || lower.contains("salesforce")
            || lower.contains("crm")
            || lower.contains("deal")
            || lower.contains("revenue growth")
            || lower.contains("upsell")
            || lower.contains("cross-sell")
        {
            return SkillDomain::Sales;
        }

        // HR keywords - comprehensive human resources coverage
        if lower.contains("hr")
            || lower.contains("human resource")
            || lower.contains("recruit")
            || lower.contains("employee")
            || lower.contains("talent")
            || lower.contains("compens")
            || lower.contains("hiring")
            || lower.contains("onboarding")
            || lower.contains("offboarding")
            || lower.contains("performance review")
            || lower.contains("performance management")
            || lower.contains("training")
            || lower.contains("learning")
            || lower.contains("development")
            || lower.contains("retention")
            || lower.contains("engagement")
            || lower.contains("culture")
            || lower.contains("diversity")
            || lower.contains("inclusion")
            || lower.contains("benefits")
            || lower.contains("hris")
            || lower.contains("workday")
            || lower.contains("adp")
            || lower.contains("bamboo")
            || lower.contains("labor relations")
            || lower.contains("compliance")
            || lower.contains("employment law")
            || lower.contains("staffing")
            || lower.contains("workforce")
        {
            return SkillDomain::HR;
        }

        // IT Support keywords - comprehensive IT support coverage
        if lower.contains("help desk")
            || lower.contains("technical support")
            || lower.contains("troubleshoot")
            || lower.contains("support ticket")
            || lower.contains("windows server")
            || lower.contains("active directory")
            || lower.contains("it support")
            || lower.contains("desktop support")
            || lower.contains("end user")
            || lower.contains("helpdesk")
            || lower.contains("service desk")
            || lower.contains("incident")
            || lower.contains("ticket")
            || lower.contains("itil")
            || lower.contains("sla")
            || lower.contains("remote support")
            || lower.contains("hardware support")
            || lower.contains("software support")
            || lower.contains("network support")
            || lower.contains("system admin")
            || lower.contains("sysadmin")
            || lower.contains("infrastructure")
            || lower.contains("backup")
            || lower.contains("restore")
            || lower.contains("patch")
            || lower.contains("antivirus")
            || lower.contains("endpoint")
        {
            return SkillDomain::ITSupport;
        }

        // Software Development keywords - comprehensive programming coverage
        if lower.contains("programming")
            || lower.contains("python")
            || lower.contains("javascript")
            || lower.contains("typescript")
            || lower.contains("java")
            || lower.contains("c++")
            || lower.contains("c#")
            || lower.contains("ruby")
            || lower.contains("php")
            || lower.contains("swift")
            || lower.contains("kotlin")
            || lower.contains("go")
            || lower.contains("rust")
            || lower.contains("scala")
            || lower.contains("software")
            || lower.contains("coding")
            || lower.contains("developer")
            || lower.contains("engineer")
            || lower.contains("full stack")
            || lower.contains("frontend")
            || lower.contains("backend")
            || lower.contains("web dev")
            || lower.contains("mobile dev")
            || lower.contains("ios dev")
            || lower.contains("android dev")
            || lower.contains("api")
            || lower.contains("rest")
            || lower.contains("graphql")
            || lower.contains("microservices")
            || lower.contains("framework")
            || lower.contains("react")
            || lower.contains("angular")
            || lower.contains("vue")
            || lower.contains("node")
            || lower.contains("spring")
            || lower.contains("django")
            || lower.contains("flask")
            || lower.contains("express")
            || lower.contains("sql")
            || lower.contains("nosql")
            || lower.contains("database")
            || lower.contains("git")
            || lower.contains("version control")
            || lower.contains("testing")
            || lower.contains("debugging")
            || lower.contains("agile")
            || lower.contains("scrum")
        {
            return SkillDomain::SoftwareDevelopment;
        }

        // Data Science keywords - comprehensive data science coverage
        if lower.contains("data scien")
            || lower.contains("machine learning")
            || lower.contains("tensorflow")
            || lower.contains("pytorch")
            || lower.contains("ml")
            || lower.contains("ai")
            || lower.contains("neural")
            || lower.contains("deep learning")
            || lower.contains("data analys")
            || lower.contains("data engineer")
            || lower.contains("big data")
            || lower.contains("analytics")
            || lower.contains("statistics")
            || lower.contains("statistical")
            || lower.contains("predictive")
            || lower.contains("model")
            || lower.contains("algorithm")
            || lower.contains("nlp")
            || lower.contains("natural language")
            || lower.contains("computer vision")
            || lower.contains("reinforcement learning")
            || lower.contains("supervised")
            || lower.contains("unsupervised")
            || lower.contains("clustering")
            || lower.contains("classification")
            || lower.contains("regression")
            || lower.contains("pandas")
            || lower.contains("numpy")
            || lower.contains("scikit")
            || lower.contains("keras")
            || lower.contains("jupyter")
            || lower.contains("spark")
            || lower.contains("hadoop")
            || lower.contains("etl")
            || lower.contains("data pipeline")
            || lower.contains("feature engineer")
            || lower.contains("data visualization")
            || lower.contains("tableau")
            || lower.contains("power bi")
        {
            return SkillDomain::DataScience;
        }

        // DevOps keywords - comprehensive DevOps coverage
        if lower.contains("devops")
            || lower.contains("jenkins")
            || lower.contains("ci/cd")
            || lower.contains("gitlab")
            || lower.contains("github actions")
            || lower.contains("circleci")
            || lower.contains("travis")
            || lower.contains("docker")
            || lower.contains("kubernetes")
            || lower.contains("k8s")
            || lower.contains("terraform")
            || lower.contains("ansible")
            || lower.contains("puppet")
            || lower.contains("chef")
            || lower.contains("containerization")
            || lower.contains("orchestration")
            || lower.contains("infrastructure as code")
            || lower.contains("iac")
            || lower.contains("cloud")
            || lower.contains("aws")
            || lower.contains("azure")
            || lower.contains("gcp")
            || lower.contains("google cloud")
            || lower.contains("amazon web services")
            || lower.contains("deployment")
            || lower.contains("automation")
            || lower.contains("monitoring")
            || lower.contains("observability")
            || lower.contains("prometheus")
            || lower.contains("grafana")
            || lower.contains("elk")
            || lower.contains("logging")
            || lower.contains("nginx")
            || lower.contains("apache")
            || lower.contains("load balancing")
            || lower.contains("scaling")
        {
            return SkillDomain::DevOps;
        }

        // Cybersecurity keywords - comprehensive security coverage
        if lower.contains("security")
            || lower.contains("cybersecurity")
            || lower.contains("infosec")
            || lower.contains("penetration test")
            || lower.contains("pentesting")
            || lower.contains("ethical hack")
            || lower.contains("vulnerability")
            || lower.contains("threat")
            || lower.contains("firewall")
            || lower.contains("encryption")
            || lower.contains("cryptography")
            || lower.contains("ssl")
            || lower.contains("tls")
            || lower.contains("authentication")
            || lower.contains("authorization")
            || lower.contains("oauth")
            || lower.contains("sso")
            || lower.contains("iam")
            || lower.contains("compliance")
            || lower.contains("gdpr")
            || lower.contains("hipaa")
            || lower.contains("pci")
            || lower.contains("iso 27001")
            || lower.contains("soc 2")
            || lower.contains("risk assessment")
            || lower.contains("incident response")
            || lower.contains("forensics")
            || lower.contains("malware")
            || lower.contains("intrusion")
            || lower.contains("siem")
        {
            return SkillDomain::Cybersecurity;
        }

        // Operations keywords - comprehensive operations coverage
        if lower.contains("operations")
            || lower.contains("ops")
            || lower.contains("supply chain")
            || lower.contains("logistics")
            || lower.contains("procurement")
            || lower.contains("inventory")
            || lower.contains("warehouse")
            || lower.contains("manufacturing")
            || lower.contains("production")
            || lower.contains("quality assurance")
            || lower.contains("quality control")
            || lower.contains("lean")
            || lower.contains("six sigma")
            || lower.contains("process improvement")
            || lower.contains("efficiency")
            || lower.contains("optimization")
            || lower.contains("vendor")
            || lower.contains("supplier")
        {
            return SkillDomain::Operations;
        }

        // Leadership keywords - comprehensive leadership coverage
        if lower.contains("leadership")
            || lower.contains("team lead")
            || lower.contains("strategic")
            || lower.contains("vision")
            || lower.contains("executive")
            || lower.contains("director")
            || lower.contains("vp")
            || lower.contains("vice president")
            || lower.contains("c-level")
            || lower.contains("ceo")
            || lower.contains("cto")
            || lower.contains("coo")
            || lower.contains("coaching")
            || lower.contains("mentoring")
            || lower.contains("delegation")
            || lower.contains("decision making")
            || lower.contains("conflict resolution")
            || lower.contains("change management")
        {
            return SkillDomain::Leadership;
        }

        // Communication keywords - comprehensive communication coverage
        if lower.contains("communication")
            || lower.contains("presentation")
            || lower.contains("public speaking")
            || lower.contains("writing")
            || lower.contains("documentation")
            || lower.contains("stakeholder")
            || lower.contains("collaboration")
            || lower.contains("interpersonal")
            || lower.contains("negotiation")
            || lower.contains("persuasion")
            || lower.contains("facilitation")
        {
            return SkillDomain::Communication;
        }

        // Project Management keywords - comprehensive PM coverage
        if lower.contains("project management")
            || lower.contains("program management")
            || lower.contains("pmp")
            || lower.contains("agile")
            || lower.contains("scrum master")
            || lower.contains("product owner")
            || lower.contains("kanban")
            || lower.contains("waterfall")
            || lower.contains("jira")
            || lower.contains("asana")
            || lower.contains("trello")
            || lower.contains("planning")
            || lower.contains("scheduling")
            || lower.contains("resource allocation")
            || lower.contains("risk management")
            || lower.contains("stakeholder management")
            || lower.contains("timeline")
            || lower.contains("milestone")
            || lower.contains("deliverable")
        {
            return SkillDomain::ProjectManagement;
        }

        // Default to General
        SkillDomain::General
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_domain_classification() {
        assert_eq!(
            SkillDomain::classify_skill("Financial Analysis"),
            SkillDomain::Finance
        );
        assert_eq!(
            SkillDomain::classify_skill("Marketing Strategy"),
            SkillDomain::Marketing
        );
        assert_eq!(
            SkillDomain::classify_skill("Python Programming"),
            SkillDomain::SoftwareDevelopment
        );
        assert_eq!(
            SkillDomain::classify_skill("Jenkins"),
            SkillDomain::DevOps
        );
    }

    #[test]
    fn test_cross_domain_penalty() {
        let finance = SkillDomain::Finance;
        let marketing = SkillDomain::Marketing;
        let software = SkillDomain::SoftwareDevelopment;
        let data_science = SkillDomain::DataScience;

        // Same domain
        assert_eq!(finance.cross_domain_penalty(&finance), 0.0);

        // Unrelated domains
        assert_eq!(finance.cross_domain_penalty(&marketing), 0.60);

        // Related domains
        assert_eq!(software.cross_domain_penalty(&data_science), 0.15);
    }
}