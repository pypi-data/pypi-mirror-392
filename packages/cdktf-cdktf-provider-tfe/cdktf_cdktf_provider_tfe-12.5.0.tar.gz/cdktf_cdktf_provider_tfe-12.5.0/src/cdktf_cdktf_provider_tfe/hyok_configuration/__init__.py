r'''
# `tfe_hyok_configuration`

Refer to the Terraform Registry for docs: [`tfe_hyok_configuration`](https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class HyokConfiguration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.hyokConfiguration.HyokConfiguration",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration tfe_hyok_configuration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        agent_pool_id: builtins.str,
        kek_id: builtins.str,
        name: builtins.str,
        oidc_configuration_id: builtins.str,
        oidc_configuration_type: builtins.str,
        kms_options: typing.Optional[typing.Union["HyokConfigurationKmsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        organization: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration tfe_hyok_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param agent_pool_id: The ID of the agent-pool to associate with the HYOK configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#agent_pool_id HyokConfiguration#agent_pool_id}
        :param kek_id: Refers to the name of your key encryption key stored in your key management service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#kek_id HyokConfiguration#kek_id}
        :param name: Label for the HYOK configuration to be used within HCP Terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#name HyokConfiguration#name}
        :param oidc_configuration_id: The ID of the TFE OIDC configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#oidc_configuration_id HyokConfiguration#oidc_configuration_id}
        :param oidc_configuration_type: The type of the TFE OIDC configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#oidc_configuration_type HyokConfiguration#oidc_configuration_type}
        :param kms_options: kms_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#kms_options HyokConfiguration#kms_options}
        :param organization: Name of the organization to which the TFE HYOK configuration belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#organization HyokConfiguration#organization}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5831e74029729f0dec72a77b31d6a8cf47fb4860c2f76b457183c702b2f8cc41)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = HyokConfigurationConfig(
            agent_pool_id=agent_pool_id,
            kek_id=kek_id,
            name=name,
            oidc_configuration_id=oidc_configuration_id,
            oidc_configuration_type=oidc_configuration_type,
            kms_options=kms_options,
            organization=organization,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a HyokConfiguration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the HyokConfiguration to import.
        :param import_from_id: The id of the existing HyokConfiguration that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the HyokConfiguration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d735c4a35b19527d1b4b12378b070fcf43b3fd59b0bbc278fc85adc777f894)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putKmsOptions")
    def put_kms_options(
        self,
        *,
        key_location: typing.Optional[builtins.str] = None,
        key_region: typing.Optional[builtins.str] = None,
        key_ring_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key_location: The location in which the GCP key ring exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_location HyokConfiguration#key_location}
        :param key_region: The AWS region where your key is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_region HyokConfiguration#key_region}
        :param key_ring_id: The root resource for Google Cloud KMS keys and key versions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_ring_id HyokConfiguration#key_ring_id}
        '''
        value = HyokConfigurationKmsOptions(
            key_location=key_location, key_region=key_region, key_ring_id=key_ring_id
        )

        return typing.cast(None, jsii.invoke(self, "putKmsOptions", [value]))

    @jsii.member(jsii_name="resetKmsOptions")
    def reset_kms_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsOptions", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="kmsOptions")
    def kms_options(self) -> "HyokConfigurationKmsOptionsOutputReference":
        return typing.cast("HyokConfigurationKmsOptionsOutputReference", jsii.get(self, "kmsOptions"))

    @builtins.property
    @jsii.member(jsii_name="agentPoolIdInput")
    def agent_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentPoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="kekIdInput")
    def kek_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kekIdInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsOptionsInput")
    def kms_options_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyokConfigurationKmsOptions"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "HyokConfigurationKmsOptions"]], jsii.get(self, "kmsOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcConfigurationIdInput")
    def oidc_configuration_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcConfigurationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcConfigurationTypeInput")
    def oidc_configuration_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcConfigurationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property
    @jsii.member(jsii_name="agentPoolId")
    def agent_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentPoolId"))

    @agent_pool_id.setter
    def agent_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8542e3b1d4c3138399d6660c36bdd11c7443050058fe93c0a43902ec4540b8bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentPoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kekId")
    def kek_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kekId"))

    @kek_id.setter
    def kek_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f13d8d92d44ba69f8b35b32c61b8af1b69495a35ce2ae91bbcec6c8d721ff5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kekId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4d3ba9b5a36b89933ac82206f48b8882d890f1a8708d021f265920a7023dc31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcConfigurationId")
    def oidc_configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcConfigurationId"))

    @oidc_configuration_id.setter
    def oidc_configuration_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75baed7bcee31d48850bc507bea146738694c79296e7babe4c102e4a20e37275)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcConfigurationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcConfigurationType")
    def oidc_configuration_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcConfigurationType"))

    @oidc_configuration_type.setter
    def oidc_configuration_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b3dbd249bde3005c6e883ac77588f7c2220e4f11b6594ea89c5461caca4dd54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcConfigurationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__944332b841feee21784ad76e7337c0e4ce01b90f7d8792336dcde093d0a7c424)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organization", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-tfe.hyokConfiguration.HyokConfigurationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "agent_pool_id": "agentPoolId",
        "kek_id": "kekId",
        "name": "name",
        "oidc_configuration_id": "oidcConfigurationId",
        "oidc_configuration_type": "oidcConfigurationType",
        "kms_options": "kmsOptions",
        "organization": "organization",
    },
)
class HyokConfigurationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        agent_pool_id: builtins.str,
        kek_id: builtins.str,
        name: builtins.str,
        oidc_configuration_id: builtins.str,
        oidc_configuration_type: builtins.str,
        kms_options: typing.Optional[typing.Union["HyokConfigurationKmsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        organization: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param agent_pool_id: The ID of the agent-pool to associate with the HYOK configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#agent_pool_id HyokConfiguration#agent_pool_id}
        :param kek_id: Refers to the name of your key encryption key stored in your key management service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#kek_id HyokConfiguration#kek_id}
        :param name: Label for the HYOK configuration to be used within HCP Terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#name HyokConfiguration#name}
        :param oidc_configuration_id: The ID of the TFE OIDC configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#oidc_configuration_id HyokConfiguration#oidc_configuration_id}
        :param oidc_configuration_type: The type of the TFE OIDC configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#oidc_configuration_type HyokConfiguration#oidc_configuration_type}
        :param kms_options: kms_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#kms_options HyokConfiguration#kms_options}
        :param organization: Name of the organization to which the TFE HYOK configuration belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#organization HyokConfiguration#organization}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(kms_options, dict):
            kms_options = HyokConfigurationKmsOptions(**kms_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dab51bbd2186d433884ff020bbd1ba3ccd1408b93a42f1f3cb0ae2b1e33effb8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument agent_pool_id", value=agent_pool_id, expected_type=type_hints["agent_pool_id"])
            check_type(argname="argument kek_id", value=kek_id, expected_type=type_hints["kek_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument oidc_configuration_id", value=oidc_configuration_id, expected_type=type_hints["oidc_configuration_id"])
            check_type(argname="argument oidc_configuration_type", value=oidc_configuration_type, expected_type=type_hints["oidc_configuration_type"])
            check_type(argname="argument kms_options", value=kms_options, expected_type=type_hints["kms_options"])
            check_type(argname="argument organization", value=organization, expected_type=type_hints["organization"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "agent_pool_id": agent_pool_id,
            "kek_id": kek_id,
            "name": name,
            "oidc_configuration_id": oidc_configuration_id,
            "oidc_configuration_type": oidc_configuration_type,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if kms_options is not None:
            self._values["kms_options"] = kms_options
        if organization is not None:
            self._values["organization"] = organization

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def agent_pool_id(self) -> builtins.str:
        '''The ID of the agent-pool to associate with the HYOK configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#agent_pool_id HyokConfiguration#agent_pool_id}
        '''
        result = self._values.get("agent_pool_id")
        assert result is not None, "Required property 'agent_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kek_id(self) -> builtins.str:
        '''Refers to the name of your key encryption key stored in your key management service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#kek_id HyokConfiguration#kek_id}
        '''
        result = self._values.get("kek_id")
        assert result is not None, "Required property 'kek_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Label for the HYOK configuration to be used within HCP Terraform.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#name HyokConfiguration#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def oidc_configuration_id(self) -> builtins.str:
        '''The ID of the TFE OIDC configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#oidc_configuration_id HyokConfiguration#oidc_configuration_id}
        '''
        result = self._values.get("oidc_configuration_id")
        assert result is not None, "Required property 'oidc_configuration_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def oidc_configuration_type(self) -> builtins.str:
        '''The type of the TFE OIDC configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#oidc_configuration_type HyokConfiguration#oidc_configuration_type}
        '''
        result = self._values.get("oidc_configuration_type")
        assert result is not None, "Required property 'oidc_configuration_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_options(self) -> typing.Optional["HyokConfigurationKmsOptions"]:
        '''kms_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#kms_options HyokConfiguration#kms_options}
        '''
        result = self._values.get("kms_options")
        return typing.cast(typing.Optional["HyokConfigurationKmsOptions"], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Name of the organization to which the TFE HYOK configuration belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#organization HyokConfiguration#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HyokConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-tfe.hyokConfiguration.HyokConfigurationKmsOptions",
    jsii_struct_bases=[],
    name_mapping={
        "key_location": "keyLocation",
        "key_region": "keyRegion",
        "key_ring_id": "keyRingId",
    },
)
class HyokConfigurationKmsOptions:
    def __init__(
        self,
        *,
        key_location: typing.Optional[builtins.str] = None,
        key_region: typing.Optional[builtins.str] = None,
        key_ring_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key_location: The location in which the GCP key ring exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_location HyokConfiguration#key_location}
        :param key_region: The AWS region where your key is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_region HyokConfiguration#key_region}
        :param key_ring_id: The root resource for Google Cloud KMS keys and key versions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_ring_id HyokConfiguration#key_ring_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a510cd0d2acc12b5983906cf664fbf75da2dbf9b02f03b459e11af9bf0bc69)
            check_type(argname="argument key_location", value=key_location, expected_type=type_hints["key_location"])
            check_type(argname="argument key_region", value=key_region, expected_type=type_hints["key_region"])
            check_type(argname="argument key_ring_id", value=key_ring_id, expected_type=type_hints["key_ring_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key_location is not None:
            self._values["key_location"] = key_location
        if key_region is not None:
            self._values["key_region"] = key_region
        if key_ring_id is not None:
            self._values["key_ring_id"] = key_ring_id

    @builtins.property
    def key_location(self) -> typing.Optional[builtins.str]:
        '''The location in which the GCP key ring exists.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_location HyokConfiguration#key_location}
        '''
        result = self._values.get("key_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_region(self) -> typing.Optional[builtins.str]:
        '''The AWS region where your key is located.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_region HyokConfiguration#key_region}
        '''
        result = self._values.get("key_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_ring_id(self) -> typing.Optional[builtins.str]:
        '''The root resource for Google Cloud KMS keys and key versions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/hyok_configuration#key_ring_id HyokConfiguration#key_ring_id}
        '''
        result = self._values.get("key_ring_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HyokConfigurationKmsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HyokConfigurationKmsOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.hyokConfiguration.HyokConfigurationKmsOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eebf9d5953b4629938c2169802d4af1136be9fa173987a7ec85f7d02aeca625a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetKeyLocation")
    def reset_key_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyLocation", []))

    @jsii.member(jsii_name="resetKeyRegion")
    def reset_key_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyRegion", []))

    @jsii.member(jsii_name="resetKeyRingId")
    def reset_key_ring_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyRingId", []))

    @builtins.property
    @jsii.member(jsii_name="keyLocationInput")
    def key_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyLocationInput"))

    @builtins.property
    @jsii.member(jsii_name="keyRegionInput")
    def key_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="keyRingIdInput")
    def key_ring_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyRingIdInput"))

    @builtins.property
    @jsii.member(jsii_name="keyLocation")
    def key_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyLocation"))

    @key_location.setter
    def key_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eec949d97d39d63a6fc30fab22e4efdc6dc5d81949426b8f9e1229ffdc84d78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyLocation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyRegion")
    def key_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyRegion"))

    @key_region.setter
    def key_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43bc9810808654c7a237a1125ead931dcee1dc580b7b1d59ec0be7408fb2e9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyRingId")
    def key_ring_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyRingId"))

    @key_ring_id.setter
    def key_ring_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b09b090f48dd878f8f51158a904647b5a1d125e649d002e8525e1250a62f50c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyRingId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyokConfigurationKmsOptions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyokConfigurationKmsOptions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyokConfigurationKmsOptions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5758914458426b7219f66d8da7f5b0355a9c7c5e694215338cff3cff4794c97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "HyokConfiguration",
    "HyokConfigurationConfig",
    "HyokConfigurationKmsOptions",
    "HyokConfigurationKmsOptionsOutputReference",
]

publication.publish()

def _typecheckingstub__5831e74029729f0dec72a77b31d6a8cf47fb4860c2f76b457183c702b2f8cc41(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    agent_pool_id: builtins.str,
    kek_id: builtins.str,
    name: builtins.str,
    oidc_configuration_id: builtins.str,
    oidc_configuration_type: builtins.str,
    kms_options: typing.Optional[typing.Union[HyokConfigurationKmsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    organization: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13d735c4a35b19527d1b4b12378b070fcf43b3fd59b0bbc278fc85adc777f894(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8542e3b1d4c3138399d6660c36bdd11c7443050058fe93c0a43902ec4540b8bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f13d8d92d44ba69f8b35b32c61b8af1b69495a35ce2ae91bbcec6c8d721ff5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4d3ba9b5a36b89933ac82206f48b8882d890f1a8708d021f265920a7023dc31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75baed7bcee31d48850bc507bea146738694c79296e7babe4c102e4a20e37275(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b3dbd249bde3005c6e883ac77588f7c2220e4f11b6594ea89c5461caca4dd54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__944332b841feee21784ad76e7337c0e4ce01b90f7d8792336dcde093d0a7c424(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dab51bbd2186d433884ff020bbd1ba3ccd1408b93a42f1f3cb0ae2b1e33effb8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    agent_pool_id: builtins.str,
    kek_id: builtins.str,
    name: builtins.str,
    oidc_configuration_id: builtins.str,
    oidc_configuration_type: builtins.str,
    kms_options: typing.Optional[typing.Union[HyokConfigurationKmsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    organization: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a510cd0d2acc12b5983906cf664fbf75da2dbf9b02f03b459e11af9bf0bc69(
    *,
    key_location: typing.Optional[builtins.str] = None,
    key_region: typing.Optional[builtins.str] = None,
    key_ring_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eebf9d5953b4629938c2169802d4af1136be9fa173987a7ec85f7d02aeca625a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eec949d97d39d63a6fc30fab22e4efdc6dc5d81949426b8f9e1229ffdc84d78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43bc9810808654c7a237a1125ead931dcee1dc580b7b1d59ec0be7408fb2e9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b09b090f48dd878f8f51158a904647b5a1d125e649d002e8525e1250a62f50c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5758914458426b7219f66d8da7f5b0355a9c7c5e694215338cff3cff4794c97(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HyokConfigurationKmsOptions]],
) -> None:
    """Type checking stubs"""
    pass
