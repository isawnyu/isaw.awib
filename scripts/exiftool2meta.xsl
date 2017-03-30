<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="#all"
    version="2.0"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:et="http://ns.exiftool.ca/1.0/' et:toolkit='Image::ExifTool 10.40"
    xmlns:ExifTool="http://ns.exiftool.ca/ExifTool/1.0/"
    xmlns:System="http://ns.exiftool.ca/File/System/1.0/"
    xmlns:File="http://ns.exiftool.ca/File/1.0/"
    xmlns:IFD0="http://ns.exiftool.ca/EXIF/IFD0/1.0/"
    xmlns:ExifIFD="http://ns.exiftool.ca/EXIF/ExifIFD/1.0/"
    xmlns:Apple="http://ns.exiftool.ca/MakerNotes/Apple/1.0/"
    xmlns:GPS="http://ns.exiftool.ca/EXIF/GPS/1.0/"
    xmlns:IFD1="http://ns.exiftool.ca/EXIF/IFD1/1.0/"
    xmlns:ICC-header="http://ns.exiftool.ca/ICC_Profile/ICC-header/1.0/"
    xmlns:ICC_Profile="http://ns.exiftool.ca/ICC_Profile/ICC_Profile/1.0/"
    xmlns:Composite="http://ns.exiftool.ca/Composite/1.0/"
    xmlns:jhove="http://hul.harvard.edu/ois/xml/ns/jhove"
    >
    
    <!-- parameters, settings, and global variables -->
    <xsl:param name="agent">script</xsl:param>
    <xsl:param name="jhove_file"/>
    <xsl:param name="iptc_name"/>
    <xsl:param name="iptc_name_prefix">isawi</xsl:param>
    <xsl:output method="xml" indent="yes" exclude-result-prefixes="#all"/>
    <xsl:variable name="photo">
        <xsl:choose>
            <xsl:when test="//ExifIFD:SceneType='Directly photographed'">yes</xsl:when>
            <xsl:otherwise>no</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:variable name="gps-date">
        <xsl:choose>
            <xsl:when test="//Composite:GPSDateTime">yes</xsl:when>
            <xsl:otherwise>no</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    
    <!-- root template: instantiate output document structure -->
    <xsl:template match="/">
        <image-info>
            <iptc_name><xsl:call-template name="make_iptc_name"/></iptc_name>
            <guid/>
            <status>draft</status>
            <license-release-verified>no</license-release-verified>
            <isaw-publish-cleared>no</isaw-publish-cleared>
            <review-notes/>
            <image-files>
                <image type="original" href="original.jpg"/>
                <image type="master" href="master.tif"/>
            </image-files>
            <info type="original">
                <xsl:apply-templates/>
                <xsl:if test=" doc-available($jhove_file)">
                    <xsl:variable name="jhove" select="document($jhove_file)"/>
                    <xsl:apply-templates select="$jhove/*"/>
                </xsl:if>
            </info>
            <info type="isaw">
                <title></title>
                <photographer>
                    <first-name/>
                    <last-name/>
                    <orcid/>
                </photographer>
                <authority/>
                <description/>
                <date-photographed/>
                <date-scanned/>
                <copyright-holder/>
                <copyright-date/>
                <copyright-contact/>
                <license/>
                <orientation/>
                <width/>
                <height/>
                <source-url href=""/>
                <dissemination-urls/>
                <geography>
                    <photographed-place/>
                    <find-place/>
                    <original-place/>
                </geography>
                <chronology/>
                <prosopography/>
                <typology/>
                <notes/>
            </info>
            <change-history>
                <change>
                    <date><xsl:value-of select="current-dateTime()"/></date>
                    <agent><xsl:value-of select="$agent"/></agent>
                    <description>Metadata file created from embedded metadata extracted from <xsl:value-of select="//System:FileName"/> using isaw.awib/scripts/exiftool2meta.xsl.</description>
                </change>
            </change-history>
        </image-info>
    </xsl:template>
    
    <!-- templates to handle specific data items of interest -->
    
    <xsl:template match="rdf:*">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="File:FileType">
        <file_type><xsl:value-of select="."/></file_type>
    </xsl:template>
    
    <xsl:template match="File:ImageWidth">
        <width><xsl:value-of select="."/></width>
    </xsl:template>

    <xsl:template match="File:ImageHeight">
        <height><xsl:value-of select="."/></height>
    </xsl:template>
    
    <xsl:template match="IFD0:Orientation">
        <orientation><xsl:value-of select="."/></orientation>
    </xsl:template>
    
    <xsl:template match="Composite:GPSDateTime">
        <date-photographed source="gps"><xsl:value-of select="."/></date-photographed>
    </xsl:template>
    
    <xsl:template match="ExifIFD:CreateDate[$photo='yes' and $gps-date='no']">
        <date-photographed source="exif"><xsl:value-of select="."/></date-photographed>
    </xsl:template>
    
    <xsl:template match="ExifIFD:CreateDate[$photo='no']">
        <date-scanned source="exif"><xsl:value-of select="."/></date-scanned>
    </xsl:template>
    
    <xsl:template match="GPS:*[count(preceding::GPS:*)=0]">
        <gps-data>
            <xsl:apply-templates select="//Composite:*[starts-with(local-name(), 'GPS')]" mode="gps_data"/>
            <xsl:apply-templates select="//GPS:*" mode="gps_data"/>
        </gps-data>
    </xsl:template>
    
    <xsl:template match="Composite:GPSLatitude" mode="gps_data">
        <latitude><xsl:value-of select="."/></latitude>
    </xsl:template>

    <xsl:template match="Composite:GPSLongitude" mode="gps_data">
        <longitude><xsl:value-of select="."/></longitude>
    </xsl:template>
    
    <xsl:template match="Composite:GPSAltitude" mode="gps_data">
        <altitude><xsl:value-of select="."/></altitude>
    </xsl:template>
    
    <xsl:template match="GPS:GPSImgDirection" mode="gps_data">
        <bearing>
            <xsl:value-of select="."/>
            <xsl:text> </xsl:text>
            <xsl:value-of select="../GPS:GPSImgDirectionRef"/></bearing>
    </xsl:template>
    
    <xsl:template match="GPS:GPSHPositioningError" mode="gps_data">
        <error><xsl:value-of select="."/></error>
    </xsl:template>
    
    <xsl:template match="jhove:jhove | jhove:repInfo">
        <xsl:apply-templates />
    </xsl:template>
    
    <xsl:template match="jhove:format">
        <jhove-format><xsl:value-of select="."/></jhove-format>
    </xsl:template>
    
    <xsl:template match="jhove:status">
        <jhove-status><xsl:value-of select="."/></jhove-status>
    </xsl:template>
    
    
    <!-- default handling for text and elements: 
           i.e., normalize text, suppress extra whitespace, suppress uninteresting elements -->
    <xsl:template match="text()">
        <xsl:variable name="normalized" select="normalize-space(.)"/>
        <xsl:if test="$normalized != ''">
            <xsl:text></xsl:text><xsl:value-of select="$normalized"/><xsl:text></xsl:text>
        </xsl:if>
    </xsl:template>
    <xsl:template match="*" mode="gps_data"/>
    <xsl:template match="*"/>
    
    <xsl:template name="make_iptc_name">
        <xsl:choose>
            <xsl:when test="$iptc_name != ''">
                <xsl:value-of select="$iptc_name"/>
            </xsl:when>
            <xsl:otherwise>
                <!-- add rules here to use exif stuff if available -->
                <xsl:value-of select="$iptc_name_prefix"/>-<xsl:value-of select=" format-dateTime(current-dateTime(), '[Y0001][M01][D01][H01][M01][s01][f0001]')"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>