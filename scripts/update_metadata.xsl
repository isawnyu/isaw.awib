<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <xsl:param name="operator">script</xsl:param>
    <xsl:param name="quiet">yes</xsl:param>
    <xsl:output indent="yes" method="xml"/>
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="image-files">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:variable name="origext">
                <xsl:for-each select="image[@type = 'original'][1]">
                    <xsl:value-of select="tokenize(@href, '\.')[last()]"/>
                </xsl:for-each>
            </xsl:variable>
            <xsl:element name="image">
                <xsl:attribute name="type">original</xsl:attribute>
                <xsl:attribute name="href">original.<xsl:value-of select="$origext"
                    /></xsl:attribute>
            </xsl:element>
            <xsl:element name="image">
                <xsl:attribute name="type">master</xsl:attribute>
                <xsl:attribute name="href">master.tif</xsl:attribute>
            </xsl:element>
            <xsl:apply-templates select="image[@type != 'thumbnail' and @type != 'review']"/>
            <xsl:apply-templates select="image[@type = 'thumbnail' or @type = 'review']"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="image[@type='thumbnail' or @type='review']" priority="20">
        <xsl:if test="$quiet!='yes'">
            <xsl:variable name="msg">
                update_metadata.xsl suppressed image with  @type=<xsl:value-of select="@type"/> and @href=<xsl:value-of select="@href"/>
            </xsl:variable>
            <xsl:message><xsl:value-of select="normalize-space($msg)"/></xsl:message>
        </xsl:if>
    </xsl:template>
    
    <xsl:template match="image[starts-with(@href, '../')]" priority="10">
        <xsl:variable name="fn" select="tokenize(@href, '\.')"/>
        <xsl:copy>
            <xsl:attribute name="type">old-<xsl:value-of select="@type"/></xsl:attribute>
            <xsl:attribute name="href">old_<xsl:value-of select="@type"/>.<xsl:value-of select="$fn[last()]"/></xsl:attribute>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="change-history">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:element name="change">
                <xsl:element name="date">
                    <xsl:value-of select=" current-dateTime()"/>
                </xsl:element>
                <xsl:element name="agent">
                    <xsl:value-of select="$operator"/>
                </xsl:element>
                <xsl:element name="description">
                    <xsl:text>This metadata file was updated using "update_metadata.xsl" from the isaw.awib toolkit.</xsl:text> 
                </xsl:element>
            </xsl:element>
            <xsl:apply-templates>
                <xsl:sort select="xs:date(date)" order="descending"/>
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="uri[starts-with(normalize-space(), 'http://pleiades.stoa.org')]">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:text>https:</xsl:text><xsl:value-of select="substring-after(normalize-space(.), 'http:')"/><xsl:text></xsl:text>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="*">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="text()">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>    
</xsl:stylesheet>