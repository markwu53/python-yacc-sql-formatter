True 1584
WITH

ChargeInstanceContext AS (
    SELECT
        trans.ID TxnID
        , tlbi.typeCode AS Context
        , tlbi.NAME AS BIName
        , chrgp.ChargeCode
        , chrgp.Subtype AS BISubtype
        , chrg.chargeGroup
        , CASE
            WHEN bi.ModificationDate IS NOT NULL THEN bi.ModificationDate
            ELSE CASE
                WHEN c.TAccountOwner = 'PolicyPeriod' THEN polper.PolicyPerEffDate
                ELSE chrg.ChargeDate
                END
            END AS TransactionEffectiveDate
    FROM bc_chargeinstancecontext cix
        INNER JOIN bc_transaction trans ON trans.ID = cix.TransactionID
        INNER JOIN bctl_transaction transtyp ON transtyp.ID = trans.Subtype
        INNER JOIN bc_charge chrg ON chrg.ID = cix.ChargeID
        INNER JOIN bc_policyperiod polper ON polper.HiddenTAccountContainerID = chrg.TAccountContainerID
        INNER JOIN bc_chargepattern chrgp ON chrgP.ID = chrg.ChargePatternID
        INNER JOIN bc_TAcctOwnerPattern c ON chrgp.TAccountOwnerPatternID = c.ID
        INNER JOIN bc_billinginstruction bi ON bi.ID = chrg.BillingInstructionID
        INNER JOIN bctl_billinginstruction tlbi ON tlbi.ID = bi.subtype
)

, ProducerContext AS (
    SELECT
        trans.ID TxnID
        , producer.Name AS ProducerName
        , trans.TransactionNumber
        , pcode.Code AS ProducerCode
        , polperiod.PolicyNumberLong AS PolicyNumber
        , pm.NAME AS ProducerPaymentMethod
        , tlpp.NAME AS ProducerPaymentType
        , prodc.NAME AS ProducerContexttype
        , tlbi.typeCode AS ChargeContext
        , chrgp.ChargeCode
        , chg.ChargeGroup
        , CASE
            WHEN bi.ModificationDate IS NOT NULL THEN bi.ModificationDate
            ELSE CASE
                WHEN c.TAccountOwner = 'PolicyPeriod' THEN polper.PolicyPerEffDate
                ELSE CASE
                    WHEN chg.ChargeDate IS NOT NULL THEN chg.ChargeDate
                    ELSE trans.TransactionDate
                    END
                END
            END AS TransactionEffectiveDate
    FROM bc_producercontext cix
        LEFT JOIN bc_producer producer ON producer.ID = cix.ProducerID
        LEFT JOIN bc_ProducerPayment prodpy ON prodpy.ID = cix.ProducerPaymentID
        LEFT JOIN bc_policycommission polcomm ON polcomm.ID = cix.PolicyCommissionID
        LEFT JOIN bc_producercode pcode ON pcode.ID = polcomm.ProducerCodeID
        LEFT JOIN bc_outgoingpayment outp ON prodpy.ID = outp.ProducerPaymentID
        LEFT JOIN bc_paymentinstrument pins ON outp.PaymentInstrumentID = pins.ID
        LEFT JOIN bctl_paymentmethod pm ON pins.PaymentMethod = pm.ID
        LEFT JOIN bc_transaction trans ON trans.ID = cix.TransactionID
        INNER JOIN bctl_transaction transtyp ON transtyp.ID = trans.Subtype
        LEFT JOIN bc_chargecommission cc ON cc.ID = cix.ChargeCommissionID
        LEFT JOIN bc_charge chg ON chg.ID = cc.ChargeID
        LEFT JOIN bc_policyperiod polper ON polper.HiddenTAccountContainerID = chg.TAccountContainerID
        LEFT JOIN bc_chargepattern chrgp ON chrgp.ID = chg.ChargePatternID
        LEFT JOIN bc_TAcctOwnerPattern c ON chrgp.TAccountOwnerPatternID = c.ID
        LEFT JOIN bc_billinginstruction bi ON bi.ID = chg.BillingInstructionID
        LEFT JOIN bctl_billinginstruction tlbi ON tlbi.ID = bi.subtype
        LEFT JOIN bctl_producerpayment tlpp ON prodpy.Subtype = tlpp.ID
        LEFT JOIN bctl_producercontext prodc ON prodc.ID = cix.subtype
        LEFT JOIN bc_policyperiod polperiod ON polperiod.ID = polcomm.PolicyPeriodID
)

SELECT
    CAST('03/01/2020' AS DATE) AS CompDt
    , CAST(trx.TransactionDate AS DATE) AS Comp2Dt
    , trx.CreateTime
    , trx.TransactionDate
    , trx.UpdateTime
    , acc.AccountNumber
    , pperiod.PolicyNumberLong
    , pcx.ProducerName AS ProducerName
    , pcx.PolicyNumber AS Producer_PolicyNumber
    , pcx.ProducerCode
    , CASE
        WHEN pperiod.PolicyNumberLong IS NOT NULL THEN pperiod.PolicyNumberLong
        WHEN pcx.PolicyNumber IS NOT NULL THEN pcx.PolicyNumber
        ELSE NULL
        END AS AllPolicyNumber
    , CASE
        WHEN acc.AccountNumber IS NOT NULL THEN acc.AccountNumber
        WHEN acc.AccountNumber IS NULL
            AND pperiod.PolicyNumberLong IS NOT NULL THEN (
            SELECT
                allacc.accountnumber
            FROM bc_account allacc
            WHERE allacc.id = (
                SELECT
                    h0policy.accountid
                FROM bc_policy h0policy
                WHERE h0policy.id = pperiod.PolicyID
            )
        )
        ELSE (
            SELECT
                all1acc.accountnumber
            FROM bc_account all1acc
            WHERE all1acc.id = (
                SELECT
                    h1policy.accountid
                FROM bc_policy h1policy
                WHERE h1policy.id = (
                    SELECT
                        h1pp.policyid
                    FROM bc_policyperiod h1pp
                    WHERE h1pp.PolicyNumberLong = pcx.PolicyNumber
                )
            )
        )
        END AS ALLAccount
    , btrx.TYPECODE AS TransactionTypeCode
    , CAST(btrx.NAME AS VARCHAR(100)) AS TransactionTYPE
    , Rtrim(tacptr.TAccountName+' '+Isnull(suffix.NAME, '')) TAccountName
    , lobcode.NAME AS LOB
    , cix.BIName AS BillingInstructionName
    , cix.BISubtype
    , CAST(COALESCE(cix.ChargeGroup, pcx.ChargeGroup) AS VARCHAR(50)) AS ChargeGroup
    , CAST(COALESCE(cix.ChargeCode, pcx.ChargeCode) AS VARCHAR(50)) AS ChargeCode
    , CAST(COALESCE(cix.Context, pcx.ChargeContext) AS VARCHAR(50)) AS ChargeContext
    , CAST(lds.NAME AS VARCHAR(50)) AS LedgersideName
    , li.PublicID AS LineItemPublicID
    , CAST(trx.TransactionNumber AS VARCHAR(100)) AS TransactionNumber
    , trx.Amount AS TransactionAmount
    , li.Amount AS LineItemAmount
    , tltacc.L_en_US AS TAccountType
    , CAST(tacpow.TAccountOwner AS VARCHAR(25)) AS TAccountOwner
    , CAST(taptype.NAME AS VARCHAR(100)) AS TAccountPatternType
    , CAST(trfrsn.NAME AS VARCHAR(100)) AS TransactionTransferReason
    , CAST(rvrsn.NAME AS VARCHAR(100)) AS TransactionReversalReason
    , CASE
        WHEN tacpow.TAccountOwner = 'Account' THEN 1
        ELSE 0
        END AS LedgerIndicator
    , CASE
        WHEN txnReversal.ID IS NULL THEN 0
        ELSE 1
        END AS TransactionReversalIndicator
    , CASE trx.Retired WHEN 0 THEN 1 ELSE 0 END AS IsActive
    , CAST(COALESCE(cix.TransactionEffectiveDate, pcx.TransactionEffectiveDate, trx.TransactionDate) AS DATETIME) AS TransactionEffectiveDate
    , li.ID AS GWRowNumber
    , ext.NAME AS AdjustmentReason
    , pcx.ProducerPaymentMethod
    , pcx.ProducerPaymentType
    , pcx.ProducerContexttype
    , NULL AS GLAccountNumber
    , NULL AS GLAccountDescription
    , bcx.ReportTo1099
    , COALESCE(pcx.ChargeGroup, cix.ChargeGroup) AS ChargeGroup
    , CASE
        WHEN btrx.TYPECODE = 'ProdCodeBonusEarned'
            AND Rtrim(tacptr.TAccountName+' '+Isnull(suffix.NAME, '')) = 'Commissions Expense' THEN bcx.LedgerAccountNo
        ELSE NULL
        END AS CommissionAdjustmentLedgerAccountNo
    , CASE
        WHEN CAST(trx.TransactionDate AS DATE) >= CAST(COALESCE(cix.TransactionEffectiveDate, pcx.TransactionEffectiveDate, trx.TransactionDate) AS DATE) THEN CAST(trx.TransactionDate AS DATE)
        ELSE CAST(COALESCE(cix.TransactionEffectiveDate, pcx.TransactionEffectiveDate, trx.TransactionDate) AS DATE)
        END AS GLTransactionDate
FROM bc_lineitem li
    JOIN bc_transaction trx ON li.TransactionID = trx.ID
    JOIN bctl_transaction btrx ON trx.Subtype = btrx.ID
    JOIN bc_taccount tac ON li.TAccountID = tac.ID
    JOIN bc_TAccountContainer tacntnr ON (tac.TAccountContainerID = tacntnr.ID)
    JOIN bc_TAccountPattern tacptr ON tac.TAccountPatternID = tacptr.ID
    JOIN bc_TAcctOwnerPattern tacpow ON tacptr.TAccountOwnerPatternID = tacpow.ID
    JOIN bctl_taccount btac ON tac.Subtype = btac.ID
    JOIN bctl_taccountcontainer tltacc ON tacntnr.Subtype = tltacc.ID
    LEFT JOIN bcx_CmsnAdjustment_Ext bcx ON bcx.id = trx.cmsnAdjustment_Ext
    LEFT JOIN bctl_cmsnadjreason_ext ext ON ext.id = bcx.AdjustmentReason
        AND ext.NAME IS NOT NULL
    LEFT JOIN bctl_ledgerside lds ON li.Type = lds.ID
    LEFT JOIN bc_account acc ON tac.TAccountContainerID = acc.HiddenTAccountContainerID
    LEFT JOIN bc_policyperiod pperiod ON tac.TAccountContainerID = pperiod.HiddenTAccountContainerID
    LEFT JOIN bc_policy policy ON pperiod.PolicyID = policy.ID
    LEFT JOIN bctl_lobcode lobcode ON policy.LOBCode = lobcode.ID
    LEFT JOIN bc_plan billpl ON billpl.ID = acc.BillingPlanID
    LEFT JOIN bc_revtrans txnReversal ON trx.ID = txnReversal.OwnerID
    LEFT JOIN bc_transfertxcontext txnTrnsfr ON COALESCE(txnReversal.ForeignEntityID, trx.ID) = txnTrnsfr.TransactionID
    LEFT JOIN bc_fundstransfer fundsTrnsfr ON txnTrnsfr.FundsTransferID = fundsTrnsfr.ID
    LEFT JOIN bctl_transferreason trfrsn ON fundsTrnsfr.Reason = trfrsn.ID
    LEFT JOIN bctl_reversalreason rvrsn ON trx.ReversalReason = rvrsn.ID
    LEFT JOIN bctl_taccounttype taptype ON tacptr.TAccountType = taptype.ID
    LEFT JOIN ChargeInstanceContext cix ON cix.TxnID = trx.ID
    LEFT JOIN ProducerContext pcx ON pcx.TxnID = trx.ID
    LEFT JOIN bctl_taccountpatternsuffix suffix ON tacptr.Suffix = Suffix.ID
WHERE CAST(trx.TransactionDate AS DATE) >= CAST('03/01/2020' AS DATE)
    AND CAST(trx.TransactionDate AS DATE) < CAST('04/01/2020' AS DATE)
    AND btrx.TYPECODE LIKE ('%Prod%')
    OR ((btrx.TYPECODE LIKE ('%Commis%')
        OR btrx.TYPECODE LIKE ('%Cmsn%')
        OR suffix.Name LIKE ('%Unearned%')
        OR tacptr.TAccountName LIKE ('%Cash%'))
        AND DateAdd(day, +1, CAST(trx.CreateTime AS DATE))
        < CAST(COALESCE(cix.TransactionEffectiveDate, pcx.TransactionEffectiveDate, trx.TransactionDate) AS DATE))
ORDER BY trx.CreateTime, trx.TransactionNumber ASC, lds.NAME DESC
