import{S as i}from"./index-CKSmRzt-.js";import"./helperFunctions-nxKLDnVn.js";import"./hdrFilteringFunctions-DjS4FS-s.js";import"./pbrBRDFFunctions-C7cC-oEd.js";import"./index-bhUlIv2p.js";const r="hdrFilteringPixelShader",e=`#include<helperFunctions>
#include<importanceSampling>
#include<pbrBRDFFunctions>
#include<hdrFilteringFunctions>
uniform float alphaG;uniform samplerCube inputTexture;uniform vec2 vFilteringInfo;uniform float hdrScale;varying vec3 direction;void main() {vec3 color=radiance(alphaG,inputTexture,direction,vFilteringInfo);gl_FragColor=vec4(color*hdrScale,1.0);}`;i.ShadersStore[r]||(i.ShadersStore[r]=e);const c={name:r,shader:e};export{c as hdrFilteringPixelShader};
//# sourceMappingURL=hdrFiltering.fragment-DshgCiM9.js.map
