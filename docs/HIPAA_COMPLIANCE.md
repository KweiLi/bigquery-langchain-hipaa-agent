# HIPAA Compliance Documentation

## Overview

This document outlines the HIPAA (Health Insurance Portability and Accountability Act) compliance measures implemented in the BigQuery LangChain Agent project.

## HIPAA Requirements

### 1. Administrative Safeguards

#### Access Control (§164.308(a)(4))
- **Role-Based Access Control (RBAC)**: Implemented in `src/security/hipaa_compliance.py`
  - Admin: Full access to all data including PHI
  - Healthcare Provider: Access to PHI for treatment purposes
  - Analyst: Limited access, no PHI
  - Read-only: View-only access to non-PHI data

- **User Authentication**: JWT-based authentication configured in settings
- **Automatic Logoff**: Configurable session timeout

#### Audit Controls (§164.308(a)(1)(ii)(D))
- **Comprehensive Audit Logging**: All data access is logged
  - User ID and timestamp
  - Action performed (READ, WRITE, DELETE, QUERY)
  - Resources accessed
  - PHI access indicators
  - Query execution details
  
- **Audit Log Storage**: Logs stored securely with configurable retention
- **Log Review**: Structured logging format (JSON) for easy analysis

#### Security Management Process (§164.308(a)(1))
- **Risk Analysis**: Regular security assessments recommended
- **Security Incident Procedures**: Error handling and logging
- **Security Updates**: CI/CD pipeline ensures timely updates

### 2. Physical Safeguards

#### Facility Access Controls (§164.310(a)(1))
When deploying on-premises:
- Physical access to servers must be restricted
- Visitor logs must be maintained
- Server rooms should have appropriate security measures

When using cloud services (GCP):
- Google Cloud Platform is HIPAA compliant with BAA
- Physical security is managed by GCP
- Documentation: https://cloud.google.com/security/compliance/hipaa

#### Workstation Security (§164.310(b))
- Application runs in isolated Docker containers
- Non-root user execution for security
- Read-only filesystem where possible

### 3. Technical Safeguards

#### Access Control (§164.312(a)(1))
- **Unique User Identification**: User ID required for all operations
- **Emergency Access**: Admin role for emergency situations
- **Automatic Logoff**: Configurable session timeout
- **Encryption and Decryption**: Implemented in `EncryptionService`

#### Audit Controls (§164.312(b))
- **Activity Logging**: All system activity logged
- **Audit Trail**: Immutable audit logs
- **Log Analysis**: Structured format for SIEM integration

#### Integrity Controls (§164.312(c)(1))
- **Data Validation**: Input validation on all queries
- **Query Sanitization**: Preventing SQL injection
- **Data Integrity**: BigQuery provides built-in integrity

#### Transmission Security (§164.312(e)(1))
- **Encryption in Transit**: TLS 1.2+ for all connections
- **GCP Encryption**: Google Cloud automatically encrypts data in transit
- **API Security**: HTTPS only for API endpoints

## Implementation Details

### Encryption

#### Data at Rest
```python
from src.security import encryption_service

# Encrypt sensitive data
encrypted = encryption_service.encrypt("patient SSN: 123-45-6789")

# Decrypt when needed
decrypted = encryption_service.decrypt(encrypted)
```

#### Data in Transit
- All BigQuery connections use TLS
- API endpoints enforce HTTPS
- Internal service communication encrypted

### Audit Logging

```python
from src.security import audit_logger

# Log PHI access
audit_logger.log_phi_access(
    user_id="doctor_123",
    record_id="patient_456",
    fields_accessed=["name", "ssn", "diagnosis"],
    purpose="treatment"
)

# Log query execution
audit_logger.log_query(
    user_id="analyst_789",
    query="SELECT COUNT(*) FROM patients",
    query_hash="abc123...",
    result_count=1,
    execution_time_ms=150.5
)
```

### Access Control

```python
from src.security import access_control

# Check if user can access PHI fields
can_access = access_control.check_phi_access(
    user_role="analyst",
    requested_fields=["name", "ssn"]
)

if not can_access:
    raise PermissionError("Insufficient privileges to access PHI")
```

## Business Associate Agreement (BAA)

### Required BAAs

1. **Google Cloud Platform**: Must have a signed BAA with Google
   - Sign BAA: https://cloud.google.com/security/compliance/hipaa
   - Verify BigQuery is covered in the BAA

2. **OpenAI (if using)**: If processing PHI through LLM
   - Note: Standard OpenAI API may not be HIPAA compliant
   - Consider: Azure OpenAI Service (HIPAA compliant)
   - Alternative: Use only for query generation, not PHI processing

### BAA Checklist

- [ ] Signed BAA with Google Cloud Platform
- [ ] BAA covers BigQuery service
- [ ] BAA covers Cloud Storage (for audit logs)
- [ ] BAA with LLM provider (if processing PHI)
- [ ] Regular BAA review and renewal
- [ ] Document all BAAs in compliance records

## Security Configuration Checklist

### Application Level

- [x] Encryption at rest enabled
- [x] Encryption in transit (TLS) enforced
- [x] Audit logging enabled
- [x] Access controls implemented
- [x] Query validation (prevent destructive operations)
- [x] PHI field detection
- [x] Rate limiting configured
- [x] Session management
- [x] Error handling (no PHI in error messages)

### Infrastructure Level

- [ ] GCP Project has appropriate IAM policies
- [ ] BigQuery dataset access restricted
- [ ] Service account least privilege
- [ ] Network security (VPC, firewall rules)
- [ ] Cloud Armor for DDoS protection
- [ ] Regular security updates
- [ ] Backup and disaster recovery
- [ ] Incident response plan

### Operational Level

- [ ] Security training for staff
- [ ] Regular security audits
- [ ] Vulnerability scanning
- [ ] Penetration testing
- [ ] Compliance monitoring
- [ ] Breach notification procedures
- [ ] Data retention policy
- [ ] Secure disposal procedures

## Data Retention and Disposal

### Retention Policy

- Default retention: 7 years (2,555 days) as per HIPAA
- Configurable via `DATA_RETENTION_DAYS`
- Audit logs: Retain for at least 6 years

### Secure Disposal

```python
# When deleting PHI:
# 1. Overwrite data multiple times
# 2. Use cryptographic erasure if encrypted
# 3. Log disposal action
# 4. Verify deletion

audit_logger.log_access(
    user_id="admin_123",
    action="DATA_DISPOSAL",
    resource="patient_record:456",
    result="SUCCESS",
    metadata={"reason": "retention_expired"}
)
```

## Breach Notification

### Breach Detection

- Monitor audit logs for unusual access patterns
- Alert on:
  - Multiple failed authentication attempts
  - Unusual query patterns
  - Large data exports
  - Access outside normal hours
  - Elevated privilege usage

### Breach Response

If a breach is detected:

1. **Immediate Actions** (within minutes)
   - Isolate affected systems
   - Preserve evidence (logs, snapshots)
   - Notify security team

2. **Within 24 Hours**
   - Assess scope of breach
   - Document affected individuals
   - Begin investigation

3. **Within 60 Days** (HIPAA requirement)
   - Notify affected individuals
   - Notify HHS (if >500 individuals)
   - Notify media (if >500 individuals in jurisdiction)

### Documentation Required

- Date and time of breach discovery
- Description of breach
- PHI involved
- Individuals affected
- Actions taken
- Contact information for inquiries

## Compliance Monitoring

### Regular Audits

- **Monthly**: Review access logs
- **Quarterly**: Security assessment
- **Annually**: Full HIPAA compliance audit

### Audit Trail Review

```bash
# Example: Extract audit logs for review
python scripts/extract_audit_logs.py \
    --start-date 2024-01-01 \
    --end-date 2024-01-31 \
    --output audit_report.json
```

### Metrics to Monitor

- PHI access frequency by user
- Failed authentication attempts
- Query execution patterns
- Data export volumes
- System errors and exceptions
- Security incidents

## Contact Information

### Security Team
- Email: security@yourorganization.com
- Phone: (555) 123-4567
- On-call: security-oncall@yourorganization.com

### Compliance Officer
- Name: [Your Compliance Officer]
- Email: compliance@yourorganization.com
- Phone: (555) 123-4568

### Breach Notification
- Emergency: breach-response@yourorganization.com
- Phone: (555) 123-4569 (24/7)

## References

- HIPAA Privacy Rule: 45 CFR Part 160 and Part 164, Subparts A and E
- HIPAA Security Rule: 45 CFR Part 160 and Part 164, Subpart C
- HIPAA Breach Notification Rule: 45 CFR Part 164, Subpart D
- HHS HIPAA Information: https://www.hhs.gov/hipaa
- Google Cloud HIPAA Compliance: https://cloud.google.com/security/compliance/hipaa

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-01 | Initial documentation | Security Team |

---

**Note**: This documentation should be reviewed and updated regularly to ensure ongoing compliance with HIPAA requirements and organizational policies.
