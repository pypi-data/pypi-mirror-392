<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  xmlns:xs="http://www.w3.org/2001/XMLSchema">
<xsl:output method="text" version="1.0" encoding="UTF-8"/>
<xsl:template match="/*">
<xsl:for-each select="IDS">
  <xsl:value-of select="@name"/>
  <xsl:if test="not(position()=last())">
    <xsl:text>&#xA;</xsl:text>
  </xsl:if>
</xsl:for-each>
</xsl:template>
</xsl:stylesheet>
