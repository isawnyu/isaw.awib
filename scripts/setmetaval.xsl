<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="#all"
    version="2.0">
    
    <xsl:param name="agent">script</xsl:param>
    <xsl:param name="target">test</xsl:param>
    <xsl:param name="value">test</xsl:param>
    <xsl:output method="xml" indent="yes" exclude-result-prefixes="#all"/>
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="*[local-name()=$target and not(ancestor::info[@type='original'])]">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="$value"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="change-history">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <change>
                <date><xsl:value-of select="current-dateTime()"/></date>
                <agent><xsl:value-of select="$agent"/></agent>
                <description>Set value of "<xsl:value-of select="$target"/>" to "<xsl:value-of select="$value"/> using isaw.awib/scripts/setmetaval.xsl.</description>
            </change>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="*">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates />
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>